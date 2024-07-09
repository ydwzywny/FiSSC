from scripts.plots import *
from scripts.sequence_stuff import *
import pickle
from scripts.graph_stuff import *


#TODO:
# change random assignment for isolated to use coneensus

class SequenceCollector():
    def __init__(self, sequences=None):
        if sequences is None:
            sequences = []
        self.picked_sequences = []
        self.working_sequences = sequences
        self.concensous = None
        self.original_size = len(sequences)
        self.original_x_count = sum([seq.count('X') for seq in sequences])

    def set_concensous(self, concensous_string):
        self.concensous = concensous_string


    def collect_picked_sequences(self, sequences):
        self.picked_sequences.extend(sequences)

    def set_working_sequences(self, sequences):
        self.working_sequences = sequences

    def remove_working_sequences(self, sequences):
        self.working_sequences.remove(sequences)

    def get_picked_sequences(self):
        return self.picked_sequences

    def get_working_sequences(self):
        return self.working_sequences
    
    def update(self):
        new_known_sequences = get_known_sequences(self.working_sequences) 
        known_sequences = new_known_sequences + self.picked_sequences
        sequences_not_covered = get_sequences_not_covered(self.working_sequences, known_sequences)
        self.set_working_sequences(sequences_not_covered)
        self.collect_picked_sequences(new_known_sequences)
    


    def print_sizes(self):
        print(f'Picked sequences: {len(self.picked_sequences)}')
        print(f'Working sequences: {len(self.working_sequences)}')
        # print number of sequences removed in %
        removed_sequences = self.original_size - len(self.working_sequences)
        print(f'Removed sequences: {round(removed_sequences/self.original_size*100, 2)}%')

        current_x_count = sum([seq.count('X') for seq in self.working_sequences])
        removed_x = self.original_x_count - current_x_count
        print(f'Removed X: {round(removed_x/self.original_x_count*100, 2)}%')

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)
    
    def load(self, path):
        with open(path, 'rb') as f:
            old = pickle.load(f)

        self.picked_sequences = old.picked_sequences
        self.working_sequences = old.working_sequences
        self.concensous = old.concensous
        self.original_size = old.original_size
        self.original_x_count = old.original_x_count



    def print_x_stats(self):
        average_number_of_x = np.mean(([seq.count('X') for seq in self.working_sequences]))
        total_number_of_x = sum([seq.count('X') for seq in self.working_sequences])
        print(f'Average number of X: {average_number_of_x}')
        print(f'Total number of X: {total_number_of_x}')

    def show_x_hist(self):
        plot_x_hist(self.working_sequences)


    def get_most_common_assignment(self):
        common_string = ''
        string_len = len(self.working_sequences[0])

        for i in range(string_len):
            freqs = {'A': 0,'G':0,'X': 0}
            for seq in self.working_sequences:
                freqs[seq[i]] += 1
            # sort letters by frequency
            sorted_freqs = sorted(freqs.items(), key=lambda x: x[1], reverse=True)

            most_common_letter = sorted_freqs[0][0]
            if most_common_letter == 'X':
                most_common_letter = sorted_freqs[1][0]

            common_string += most_common_letter

    

    def random_assignment_for_isolated(self):
        graph = build_graph(self.working_sequences)
        isolated_nodes = [node for node in graph.nodes() if graph.degree(node) == 0]
        assigned_nodes = [random_assignment(node) for node in isolated_nodes]

        self.collect_picked_sequences(assigned_nodes)
        



    def concensous_assignment_for_isolated(self, concensous_string):
        graph = build_graph(self.working_sequences)
        isolated_nodes = [node for node in graph.nodes() if graph.degree(node) == 0]
        assigned_nodes = [concensous_assignment(node, concensous_string) for node in isolated_nodes]

        self.collect_picked_sequences(assigned_nodes)




    


    # TODO: add way to use concensous to generate original strings
