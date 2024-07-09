import os
import pandas as pd
from scripts.sequence_stuff import *
from scripts.plots import *
from scripts.collector import *
import pickle
from collections import deque

# TODO:
# When collecting from clashing sequences, make sure to assign the X to cocnensus
# 

class Filter:
    def __init__(self, sequences, log_file_path= 'filter_log.csv', do_logs = True):
        self.initial_sequences_len = len(sequences)
        self.initial_x_count = sum([seq.count('X') for seq in sequences])
        self.collectors = deque()
        self.collectors.append(SequenceCollector(sequences))
        self.history = []
        self.finished_collectors = []
        self.final_working_sequences = []
        self.final_picked_sequences = []
        self.log_file_path = log_file_path
        self.reset_log_file()
        self.current_collector = None
        self.concensous_string = self.calculate_concensous_string(sequences)
        columns = ['Method', 'Working', 'Picked', 'X count', 'Active collectors', 'Finished collectors']
        self.log_row_to_file(','.join(columns))
        self.do_logs = do_logs


    def calculate_concensous_string(self, sequences):
        # Convert sequences to a NumPy array
        array = np.array([list(seq) for seq in sequences])
        
        # Initialize the consensus string
        concensous = ''
        
        for i in range(array.shape[1]):
            # Get the column of characters at position i
            column = array[:, i]
            # Find the unique characters and their counts
            unique, counts = np.unique(column, return_counts=True)
            # Sort characters by count in descending order
            sorted_indices = np.argsort(-counts)
            sorted_unique = unique[sorted_indices]
            sorted_counts = counts[sorted_indices]
            
            # Pick the second most popular character if the most popular is 'X'
            if sorted_unique[0] == 'X' and len(sorted_unique) > 1:
                concensous += sorted_unique[1]
            else:
                concensous += sorted_unique[0]
            
        return concensous
    

    def reset_log_file(self):
        with open(self.log_file_path, 'w') as f:
            f.write("")

    def get_all_collectors(self):
        if self.current_collector is not None:
            return self.finished_collectors + list(self.collectors) + [self.current_collector]
        else:
            return self.finished_collectors + list(self.collectors)

    def get_total_x_count(self, current_collector=None):
        sum = 0
        for collector in self.get_all_collectors():
            for sequence in collector.get_working_sequences():
                sum += sequence.count('X')



        return sum
    
    def get_total_working_sequences(self, current_collector=None):
        sum = 0
        for collector in self.get_all_collectors():
            sum += len(collector.get_working_sequences())
        return sum
    
    def get_total_picked_sequences(self, current_collector=None):
        sum = 0
        for collector in self.get_all_collectors():
            sum += len(collector.get_picked_sequences())
        return sum
    
    def print_progress(self):
        print(f"Working sequences: {self.get_total_working_sequences()}")
        print(f"Picked sequences: {self.get_total_picked_sequences()}")
        print(f"X count: {self.get_total_x_count()}")
        print(f"Working sequences reduction: {round((self.initial_sequences_len - self.get_total_working_sequences())/self.initial_sequences_len*100, 2)}%")
        print(f"X count reduction: {round((self.initial_x_count - self.get_total_x_count())/self.initial_x_count*100, 2)}%")
        print(f"Active collectors: {len(self.collectors)}")
        print(f"Finished collectors: {len(self.finished_collectors)}")
        print("")
        
    def update_history_and_log(self, method,current_collector):
        x_count = self.get_total_x_count(current_collector)
        sequence_count = self.get_total_working_sequences(current_collector)
        picked_sequence_count = self.get_total_picked_sequences(current_collector)
        self.history.append((method, sequence_count, picked_sequence_count,x_count))
        if self.do_logs:
            if method != "Initial":
                # if not initial then we already have a current collector dequeued
                self.log_row_to_file(f"{method},{sequence_count},{picked_sequence_count},{x_count},{len(self.collectors)+1},{len(self.finished_collectors)}")
            else:
                self.log_row_to_file(f"{method},{sequence_count},{picked_sequence_count},{x_count},{len(self.collectors)},{len(self.finished_collectors)}")

    def log_row_to_file(self, row):
        with open(self.log_file_path, 'a') as f:
            f.write(row + '\n')

    def print_history(self):
        for i, (method, sequence_count, picked_sequence_count, x_count) in enumerate(self.history):
            print(f"Method {i+1}: {method} - Working: {sequence_count} - Picked: {picked_sequence_count} - X Count: {x_count}")

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)
    
    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)
        
    def update_knowns(self, collector):
        collector.update()
        self.update_history_and_log("Update Knowns", collector)

    def save_working_csv(self, path):
        combined_df = pd.DataFrame()
        for i, final_working in enumerate(self.final_working_sequences):
            df = pd.DataFrame(final_working, columns=['Sequence'])
            df['CC'] = i
            combined_df = pd.concat([combined_df, df])
        combined_df.to_csv(path, index=False)

    def save_picked_csv(self, path):
        df = pd.DataFrame(self.final_picked_sequences, columns=['Sequence'])
        df.to_csv(path, index=False)


    def remove_less_specific(self, collector):
        more_specific_sequences, less_specific_sequences = get_more_specific_sequences(collector.get_working_sequences())
        collector.set_working_sequences(more_specific_sequences)
        self.update_history_and_log("Remove Less Specific", collector)


    def pick_clashing(self, collector):
        clashing_sequences, non_clashing_sequences = get_clashing_non_clashing(collector.get_working_sequences())
        collector.set_working_sequences(non_clashing_sequences)
        collector.collect_picked_sequences(clashing_sequences)
        self.update_history_and_log("Pick Clashing", collector)

    def pick_must_have_assignments(self, collector, up_to_k=6):
        only_possible_assignment = get_only_possible_assignments(collector.get_working_sequences(), up_to_k=up_to_k)
        collector.collect_picked_sequences(only_possible_assignment)
        self.update_history_and_log("Pick Must Have Assignments", collector)
        self.update_knowns(collector)


    
    def split_to_cc(self,collector):
        graph = build_graph(collector.get_working_sequences())
        connected_components = list(nx.connected_components(graph))
        sub_collectors = []
        for component in connected_components:
            sub_collectors.append(SequenceCollector(component))
        
        # the first sub_collector will remain the list of all selected sequences, it is not used for filtering but to keep track of the selected sequences
        sub_collectors[0].collect_picked_sequences(collector.get_picked_sequences())

        return sub_collectors



    def merge_lonely_sequences(self, collector):
        new_all_seqs = merge_lonely_from_graph(collector)
        collector.set_working_sequences(new_all_seqs)
        self.update_history_and_log("Merge Lonely Sequences", collector)
        self.update_knowns(collector)

    def assign_concensous_for_isolated(self, collector):
        collector.concensous_assignment_for_isolated(self.concensous_string)
        self.update_history_and_log("Assign Concensous for Isolated", collector)
        self.update_knowns(collector)

    def apply_local_concensous(self, collector):
        sequences_after_local_consensus = local_concensous(collector.get_working_sequences())
        collector.set_working_sequences(sequences_after_local_consensus)
        self.update_history_and_log("Apply Local Concensous", collector)


    def do_filter(self):
        # first filter
        self.filter_loop()
        for collector in self.finished_collectors:
            working_seqs = collector.get_working_sequences()
            picked_seqs = collector.get_picked_sequences()
            self.final_working_sequences.append(working_seqs) #Cuz we need to treat each separately
            self.final_picked_sequences.extend(picked_seqs)

    

        return self.final_working_sequences, self.final_picked_sequences, self.history

    def filter_loop(self):
        self.update_history_and_log("Initial", self.collectors[0]) #TODO: make sure works

        while len(self.collectors) > 0:
            self.print_progress()
            self.current_collector = self.collectors.pop()
            initial_sequence_n = len(self.current_collector.get_working_sequences())
            self.update_knowns(self.current_collector)
            self.remove_less_specific(self.current_collector)
            #self.pick_clashing(self.current_collector)
            self.pick_must_have_assignments(self.current_collector)
            self.merge_lonely_sequences(self.current_collector)
            self.assign_concensous_for_isolated(self.current_collector)
            self.apply_local_concensous(self.current_collector)
            if len(self.current_collector.get_working_sequences()) > 1:
                sub_collectors = self.split_to_cc(self.current_collector)
            else:
                sub_collectors = []
            
            # If we split we always continue
            if len(sub_collectors) > 1:
                for sub_collector in sub_collectors:
                    self.collectors.append(sub_collector)
            # otherwise we check if we should continue
            else:
                if len(self.current_collector.get_working_sequences()) == initial_sequence_n or len(self.current_collector.get_working_sequences()) == 0:
                    self.finished_collectors.append(self.current_collector)
                else:
                    self.collectors.append(self.current_collector)
            self.current_collector = None
        

