import pandas as pd
from scripts.sequence_stuff import *
from scripts.plots import *
from scripts.collector import *
from scripts.filtering import *
from scripts.graph_stuff import *
import time





def maximal_independent_set(G):
    # Create an empty set for the independent set
    independent_set = set()

    # Sort the nodes by degree in ascending order
    sorted_nodes = sorted(G.nodes(), key=lambda x: G.degree(x))

    # Add nodes to the independent set one by one
    for node in sorted_nodes:
        # Check if the node can be added to the independent set
        if all(neighbor not in independent_set for neighbor in G.neighbors(node)):
            independent_set.add(node)
    
    return independent_set


def is_clique(G, nodes):
    # Check if the subgraph induced by nodes is a clique
    return all(node in G.neighbors(neighbor) for node in nodes for neighbor in nodes if node != neighbor)

def is_neighbor_to_all(G, temp_clique, node):
    return all(node in G.neighbors(neighbor) for neighbor in temp_clique)



def clique_cover(G):
    # Create an empty set for the cover
    cover_size=  0

    # Sort the nodes by degree in descending order
    sorted_nodes = sorted(G.nodes(), key=lambda x: -G.degree(x))
    added_nodes = set()

    # Add cliques to the cover one by one
    for i, node in enumerate(sorted_nodes):
        if i % 100 == 0:
            print(f'Processing node {i} out of {len(sorted_nodes)}, added {len(added_nodes)} nodes to the cover so far.')
        # check if thge node was already added
        if node in added_nodes:
            continue

        # else we add it and a clique around it
        temp_clique = [node]
        cover_size += 1


        # order its neighbors by degree
        neighbors = sorted(G.neighbors(node), key=lambda x: -G.degree(x))

        # remove neighbors that are already in the cover
        neighbors = [neighbor for neighbor in neighbors if neighbor not in added_nodes]

        # Try adding neighbors to the clique
        for neighbor in neighbors:
            if is_neighbor_to_all(G, temp_clique, neighbor):
                temp_clique.append(neighbor)

        # Add the clique to the cover
        added_nodes.update(temp_clique)

    return cover_size



def greedy_solutions(experiment_name):
    starting_time = time.time()
    sequences = pd.read_csv(f'data/{experiment_name}.csv')['Sequence'].values
    collector=  SequenceCollector(sequences)
    collector.update()
    uncovered_sequences = collector.get_working_sequences()
    covering_sequences = collector.get_picked_sequences()
    # make unique
    covering_sequences = list(set(covering_sequences))

    graph = build_graph(uncovered_sequences)
    print(f'Graph built in {time.time()-starting_time} seconds')

    starting_time = time.time()
    print(f'Running greedy MIS on {experiment_name} with {len(uncovered_sequences)} sequences')
    indepedent_set_size = len(maximal_independent_set(graph)) + len(covering_sequences)
    print(f'MIS time: {time.time()-starting_time} seconds')

    starting_time = time.time()
    print(f'Running greedy clique cover on {experiment_name} with {len(uncovered_sequences)} sequences')
    cover_size = clique_cover(graph)+ len(covering_sequences)
    print(f'Clique cover time: {time.time()-starting_time} seconds')

    print(f'MIS size: {indepedent_set_size}')
    print(print(f'Clique cover size: {cover_size}'))

    # save the sizes to a file
    with open(f'output/{experiment_name}_greedy_results.txt', 'w') as f:
        f.write(f'MIS size: {indepedent_set_size}\n')
        f.write(f'Clique cover size: {cover_size}\n')

                    
