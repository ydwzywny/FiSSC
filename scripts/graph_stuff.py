import networkx as nx
from scripts.sequence_stuff import do_sequences_clash
from scripts.sequence_stuff import *



def build_graph(sequences):
    G = nx.Graph()
    G.add_nodes_from(sequences)
    max_index = len(sequences) - 1

    for i in range(max_index):
        if i % 100 == 0:
            print(f"Adding edges for sequence {i}/{max_index}")
        for j in range (i+1, max_index+1):
            if not do_sequences_clash(sequences[i], sequences[j]):
                G.add_edge(sequences[i], sequences[j])
    return G

def local_concensous(sequences):
    graph = build_graph(sequences)


    to_concensous = {}

    for sequence in sequences:
        new_sequence = sequence
        length = len(sequence)
        neighbors = list(graph.neighbors(sequence))
        for position in range(length):
            if sequence[position] != 'X':
                continue
            # check if all neighbors have the same letter in the same position
            letters = set()
            for neighbor in neighbors:
                letters.add(neighbor[position])
            if len(letters) == 1:
                new_sequence = new_sequence[:position] + list(letters)[0] + new_sequence[position+1:]
        to_concensous[sequence] = new_sequence

    new_sequences = []
    for sequence in sequences:
        new_sequences.append(to_concensous[sequence])
    
    return new_sequences

def merge_lonely_from_graph(collector):
    graph = build_graph(collector.get_working_sequences())

    # get all sequences in graph
    sequences = list(graph.nodes())
    lonely_sequences_mapping = {}
    sequences_to_remove = []

    print("Finding lonely sequences")

    for node in sequences:
        remove_seq = False
        neighbors = list(graph.neighbors(node))
        # if has 1 neighbor with 1 neighbor - > skip (will be a CC of 2 and is easy to solve anyways)
        if len(neighbors) == 1 and len(list(graph.neighbors(neighbors[0]))) == 1:
            continue
    

        for neighbor in neighbors:
            if len(list(graph.neighbors(neighbor))) == 1: 
                lonely_sequences_mapping[neighbor] = merge_sequences(neighbor, node)
                remove_seq = True


        if remove_seq:
            sequences_to_remove.append(node)

    new_all_seqs = []
    for seq in sequences:
        if seq not in sequences_to_remove:
            if seq not in lonely_sequences_mapping:
                new_all_seqs.append(seq)
            else:
                new_all_seqs.append(lonely_sequences_mapping[seq])
    
    return new_all_seqs

