import pandas as pd
from scripts.sequence_stuff import *
from scripts.plots import *
from scripts.collector import *
from scripts.filtering import *


def validate_solution(original_sequences_path, picked_sequences_path):

    original_sequences = pd.read_csv(original_sequences_path)['Sequence'].values
    picked_sequences = pd.read_csv(picked_sequences_path)['Sequence'].values


    collector = SequenceCollector(original_sequences)
    collector.collect_picked_sequences(picked_sequences)
    collector.update()


    if len(collector.get_working_sequences()) == 0:
        print('Solution is valid, all sequences are covered')
    else:
        print(f'Solution is not valid, {len(collector.get_working_sequences())} sequences are not covered')
