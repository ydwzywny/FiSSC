import time
import gurobipy as gp
from gurobipy import Model, GRB, quicksum
import numpy as np
import networkx as nx
import pandas as pd
import json
from scripts.collector import *
from scripts.graph_stuff import *
from scripts.sequence_stuff import *
import os
import pickle

def convert_sequences_to_array(sequences):

    # Convert to numpy array
    sequence_array = np.array(sequences)


    return sequence_array

def get_model():
  with open('gurobi.json', 'r') as json_file:
    params = json.load(json_file)
  env = gp.Env(params=params)

  # Create the model within the Gurobi environment
  model = gp.Model('min-sum', env=env)

  return model

def find_connected_nodes(graph):
    connected_nodes = {}
    for node in graph.nodes():
        connected_nodes[node] = [n for n in list(graph.neighbors(node))]
    return connected_nodes


def solve_maximum_independent_set(connected_nodes,args):
    """
    Solves the Maximum Independent Set problem using Integer Linear Programming (ILP).

    Parameters:
    graph (dict): Adjacency list representation of the graph where each key is a node and the value is a list of neighbors.

    Returns:
    list: A list of nodes that form the maximum independent set.
    """

    model = get_model()

    # Create variables
    x = {}
    for node in connected_nodes.keys():
        x[node] = model.addVar(vtype=GRB.BINARY, name=f"x_{node}")

    # Set objective: Maximize the sum of x_i
    model.setObjective(quicksum(x[node] for node in connected_nodes.keys()), GRB.MAXIMIZE)

    # Add constraints: For every edge (i, j), x_i + x_j <= 1
    for node in connected_nodes.keys():
        for neighbor in connected_nodes[node]:
            model.addConstr(x[node] + x[neighbor] <= 1)

    model.setParam('Threads', args.threads) 
    model.setParam('Seed', 42) 

    if args.ILP_time_restriction_in_minutes > 0:
        model.setParam(GRB.Param.TimeLimit, args.ILP_time_restriction_in_minutes*60)



    # Optimize model
    model.optimize()

    # Retrieve the maximum independent set
    independent_set = []
    if model.Status in [GRB.OPTIMAL, GRB.TIME_LIMIT]:
        for node in connected_nodes.keys():
            if x[node].X > 0.5:
                independent_set.append(node)

    return independent_set



def mis_ilp_solution(experiment_name,args):
    sequences = pd.read_csv(f'data/{experiment_name}.csv')['Sequence'].values
    collector=  SequenceCollector(sequences)
    collector.update()
    uncovered_sequences = collector.get_working_sequences()
    previously_picked_sequences = len(collector.get_picked_sequences())


    sequences_array = convert_sequences_to_array(uncovered_sequences)

    graph = build_graph(sequences_array)

    connected_nodes = find_connected_nodes(graph)

    max_IS_seq = solve_maximum_independent_set(connected_nodes,args)

    
    ilp_picked_sequences = len(max_IS_seq)
    total_picked_sequences = previously_picked_sequences + ilp_picked_sequences

    print(f"Total picked sequences: {total_picked_sequences}")

    with open(f'{experiment_name}_mis_ilp_results.txt',"w") as out:
        out.write(f"Picked sequences: {total_picked_sequences}\n")




def mis_ilp_solution_p1(experiment_name,args):
    sequences = pd.read_csv(f'data/{experiment_name}.csv')['Sequence'].values
    collector=  SequenceCollector(sequences)
    collector.update()
    uncovered_sequences = collector.get_working_sequences()
    previously_picked_sequences = len(collector.get_picked_sequences())



    sequences_array = convert_sequences_to_array(uncovered_sequences)

    graph = build_graph(sequences_array)

    connected_nodes = find_connected_nodes(graph)

    # create /temp folder
    if not os.path.exists('temp'):
        os.makedirs('temp')

    # save them as pickle
    with open(f'temp/{experiment_name}_connected_nodes.pickle', 'wb') as f:
        pickle.dump(connected_nodes, f)

    # save previously picked sequences
    with open(f'temp/{experiment_name}_previously_picked_sequences.pickle', 'wb') as f:
        pickle.dump(previously_picked_sequences, f)

    # save sequences array
    with open(f'temp/{experiment_name}_sequences_array.pickle', 'wb') as f:
        pickle.dump(sequences_array, f)




def mis_ilp_solution_p2(experiment_name,args):
    # load connected nodes
    with open(f'temp/{experiment_name}_connected_nodes.pickle', 'rb') as f:
        connected_nodes = pickle.load(f)

    # load previously picked sequences
    with open(f'temp/{experiment_name}_previously_picked_sequences.pickle', 'rb') as f:
        previously_picked_sequences = pickle.load(f)

    # load sequences array
    with open(f'temp/{experiment_name}_sequences_array.pickle', 'rb') as f:
        sequences_array = pickle.load(f)
    
    max_IS_seq = solve_maximum_independent_set(connected_nodes,args)

    ilp_picked_sequences = len(max_IS_seq)
    total_picked_sequences = previously_picked_sequences + ilp_picked_sequences

    print(f"Total picked sequences: {total_picked_sequences}")

    with open(f'{experiment_name}_mis_ilp_results.txt',"w") as out:
        out.write(f"Picked sequences: {total_picked_sequences}\n")

    
