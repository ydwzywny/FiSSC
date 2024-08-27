import time
from collections import defaultdict
import gurobipy as gp
from gurobipy import Model, GRB, quicksum
from Bio import SeqIO
import random
import numpy as np
import random
import networkx as nx
import pandas as pd
import time
import json


def read_sequences_as_array(working_sequences_file_path):

    df = pd.read_csv(working_sequences_file_path)
    sequences = list(df["Sequence"])
    num_sequences= len(sequences)
    cc = list(df["CC"])

    selected_sequences = sequences
    selected_cc = cc

    # Convert to numpy array
    sequence_array = np.array([list(seq) for seq in selected_sequences])

    P = len(sequence_array[0])

    # convert to binary representation 0/1
    sequence_array = [''.join('1' if seq[pos] == 'G' else '0' if seq[pos] == 'A' else '.' for pos in range(P))
    for seq in sequence_array]

    return sequence_array, selected_cc


def group_indices_by_value(lst):

    value_to_indices = defaultdict(list)

    # Traverse the list and group indices by values
    for index, value in enumerate(lst):
        value_to_indices[value].append(index)

    # Convert defaultdict to a regular dict for cleaner output
    return dict(value_to_indices)

def fill_in_assignments(cover_tuples,working_sequences_path):

    working_sequences= pd.read_csv(working_sequences_path)["Sequence"].values
    cover_sequences=[]
    for idx,assignments in cover_tuples:
        sequence = list(working_sequences[idx])
        x_positions = [j for j in range(len(sequence)) if sequence[j]=='X']
        for pos,assignment in zip(x_positions,assignments):
            sequence[pos]=assignment
        cover_sequences.append(''.join(sequence))

    return cover_sequences

def get_model():
  with open('gurobi.json', 'r') as json_file:
    params = json.load(json_file)
    
  env = gp.Env(params=params)

  # Create the model within the Gurobi environment
  model = gp.Model('min-sum', env=env)

  return model


def do_sequences_clash(seq1, seq2):

    return any(l1 != l2 and l1 != '.' and l2 != '.' for l1, l2 in zip(seq1, seq2))

def build_graph(sequences):

    G = nx.Graph()
    max_index = len(sequences)
    G.add_nodes_from(range(max_index))

    for i in range(max_index):
        if i % 100 == 0:
            print(f"Adding edges for sequence {i}/{max_index}")
        for j in range (i+1, max_index):
            if not do_sequences_clash(sequences[i], sequences[j]):
                G.add_edge(i, j)
    return G


def find_connected_nodes(graph):
    connected_nodes = {}
    for node in graph.nodes():
        connected_nodes[int(node)] = [int(n) for n in list(graph.neighbors(node))]
    return connected_nodes




def solve_cover(sequences,connected_nodes, args):
    sequence_cover = []
    sequences_idx = [int(seq) for seq in connected_nodes.keys()]

    print("Num sequences: ",len(sequences_idx))

    P=len(sequences[0]) # num of variable positions

    model = get_model()

    # Xij is 1 if bit j is 1 is in cover instance i, else 0
    x = {}

    # iterate over all sequences to create Xij var for every x edit positions
    for i in sequences_idx:
        x_positions = [j for j in range(P) if sequences[i][j]=='.']
        for j in x_positions:
            x[(i,j)] = model.addVar(vtype=GRB.BINARY)

    C = {}
    # indicator variable for each sequence in output cover
    for i in sequences_idx:
        C[i] = model.addVar(vtype=GRB.BINARY)

    ## objective - minimize number of sequences in cover
    model.setObjective(quicksum(C[i] for i in sequences_idx), GRB.MINIMIZE)

    # iterate over each sequence and its neighbors
    for seq, neighbors in connected_nodes.items():

        O={}

        sequence_ls=neighbors+[seq] # neighbor list

        # iterate over all neighbors i of seq
        for i in sequence_ls:
            # O[i] indicates if neighbor i covers seq
            O[i] = model.addVar(vtype=GRB.BINARY)

            matches = []

            # only look at variable X(A/G) positions in neighbor sequence
            x_positions = [j for j in range(P) if sequences[i][j] == '.']

            ## iterate over all X positions in neighbor and check match with current sequence
            for j in x_positions:
                bit_match = model.addVar(vtype=GRB.BINARY)
                if sequences[seq][j] == '1':
                    model.addConstr(bit_match == x[(i, j)])
                elif sequences[seq][j] == '0':
                    model.addConstr(bit_match == 1 - x[(i, j)])
                else:
                    continue  # Skip positions with '.' in seq
                matches.append(bit_match)

            matches.append(C[i])

            ## all bits must match and indicator c[i] must be 1 for sequence to be covered by neighbor i (AND opearator)
            model.addGenConstrAnd(O[i], matches)

        ## ensure sequence is covered by at least one neighbor i
        model.addConstr(quicksum(O[i] for i in sequence_ls) >= 1)

    model.setParam('Threads', args.threads) 
    model.setParam('Seed', 42) 

    if args.ILP_time_restriction_in_minutes > 0:
        model.setParam(GRB.Param.TimeLimit, args.ILP_time_restriction_in_minutes*60)
    

    ## optimize model
    model.optimize()

    # return cover solution
    if model.Status in [GRB.OPTIMAL, GRB.TIME_LIMIT]:
        for i in sequences_idx:
            if C[i].X>0.5:
                x_positions = [j for j in range(P) if sequences[i][j] == '.']
                sequence = ''
                for j in x_positions :
                    if x[(i, j)].X > 0.5:  # If bit j is set in sequence i
                        sequence += 'G'
                    else:
                        sequence += 'A'
                sequence_cover.append((i,sequence))

        return sequence_cover
    else:
        return None


def ilp_solution(working_sequences_file_path, picked_sequences_file_path, time_limit_in_minutes, experiment_name, args):
   
    # check size of workign sequences
    df = pd.read_csv(working_sequences_file_path)
    num_sequences = len(df)
    if num_sequences > 0:

        # retrieve sequence and their connected components from file
        variable_sequences, CC = read_sequences_as_array(working_sequences_file_path)

        # divide into connected components
        connected_components = group_indices_by_value(CC)
        #print(connected_components)

        ## create graph
        G = build_graph(variable_sequences)

        # find neighbor list for each sequence
        connected_nodes = find_connected_nodes(G)

        total_sequence_cover=[]

        # run ILP solver on every connected component
        for CC in connected_components.values():
            #print(CC)
            #print(connected_nodes)
            #print(len(connected_nodes))
            #print(len(CC))
            neighbor_ls = {i:connected_nodes[i] for i in CC}
            component_cover = solve_cover(variable_sequences,neighbor_ls, args)
            total_sequence_cover+=component_cover

        total_sequence_cover = fill_in_assignments(total_sequence_cover,working_sequences_file_path)

        # get all the sequences from picked_sequences_file_path in the Sequence column
        picked_previously = pd.read_csv(picked_sequences_file_path)["Sequence"].values

        # combine the sequences from the ILP solution and the picked sequences
        final_picked_sequences = np.concatenate((picked_previously, total_sequence_cover))
    else:
        final_picked_sequences = pd.read_csv(picked_sequences_file_path)["Sequence"].values

    size_before = len(final_picked_sequences)

    # remove duplicates
    final_picked_sequences = np.unique(final_picked_sequences)

    size_after = len(final_picked_sequences)
    print(f"Removed {size_before - size_after} duplicates")

    # save the final picked sequences to a file
    final_picked_sequences_df = pd.DataFrame(data={"Sequence": final_picked_sequences})
    final_picked_sequences_df.to_csv(f'output/{experiment_name}_picked_sequences.csv', index=False)

    print(f"Saved picked sequences to output/{experiment_name}_picked_sequences.csv")

