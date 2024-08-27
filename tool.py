import pandas as pd
import time

from scripts.sequence_stuff import *
from scripts.plots import *
from scripts.collector import *
from scripts.filtering import *
from scripts.args import *
from scripts.ilp import *
from scripts.utils import *
from scripts.preprocessing import *
from scripts.greedy_algorithms import *
from scripts.validation import *
from scripts.mis_ilp import *

#TODO: change terminology - sequence/read etc

def debug_ilp(args, experiment_name, file_path):
    starting_time = time.time()
    print(f'Working on {experiment_name}, {file_path}')
    working_sequences_file_path = f'data/{experiment_name}_filtered_working.csv'
    picked_sequences_file_path = f'data/{experiment_name}_filtered_picked.csv'
    ilp_solution(working_sequences_file_path, picked_sequences_file_path, args.ILP_time_restriction_in_minutes, experiment_name, args)
    print(f'{experiment_name} done ILP in {time.time()-starting_time} seconds')


def test_preprocess(file_path, experiment_name):    
    print(f'Preprocessing {experiment_name}')
    starting_time = time.time()
    preprocess(file_path, experiment_name)
    print(f'{experiment_name} done preprocessing in {time.time()-starting_time} seconds')


def paper_algorithm(args, experiment_name, file_path):
    starting_time = time.time()
    print(f'Working on {experiment_name}, {file_path}')
    preprocessed_file = f'data/{experiment_name}.csv'
    sequences = pd.read_csv(preprocessed_file)['Sequence'].values
    # create logs folder
    if not os.path.exists('logs'):
        os.makedirs('logs')
    filter = Filter(sequences, log_file_path=f'logs/{experiment_name}_filter_log.csv', do_logs=args.do_logs)
    final_working_sequences, final_picked_sequences, history = filter.do_filter()


    working_sequences_file_path = f'data/{experiment_name}_filtered_working.csv'
    picked_sequences_file_path = f'data/{experiment_name}_filtered_picked.csv'
    filter.save_working_csv(working_sequences_file_path)
    filter.save_picked_csv(picked_sequences_file_path)
    print(f'{experiment_name} done filtering in {time.time()-starting_time} seconds')


    starting_time = time.time()
    ilp_solution(working_sequences_file_path, picked_sequences_file_path, args.ILP_time_restriction_in_minutes, experiment_name, args)
    print(f'{experiment_name} done ILP in {time.time()-starting_time} seconds')

    validate_solution(preprocessed_file, f'output/{experiment_name}_picked_sequences.csv')



def greedy_algorithms(args, experiment_name, file_path):
    greedy_solutions(experiment_name)

def mis_ilp_algorithm(args, experiment_name, file_path):
    starting_time = time.time()
    mis_ilp_solution(experiment_name,args)
    print(f'{experiment_name} done mis_ilp in {time.time()-starting_time} seconds')

def mis_ilp_algorithm_p1(args, experiment_name, file_path):
    starting_time = time.time()
    mis_ilp_solution_p1(experiment_name,args)
    print(f'{experiment_name} done mis_ilp_p1 in {time.time()-starting_time} seconds')

def mis_ilp_algorithm_p2(args, experiment_name, file_path):
    starting_time = time.time()
    mis_ilp_solution_p2(experiment_name,args)
    print(f'{experiment_name} done mis_ilp_p2 in {time.time()-starting_time} seconds')


def validate_fissc_solution(experiment_name):
    preprocessed_file = f'data/{experiment_name}.csv'
    validate_solution(preprocessed_file, f'output/{experiment_name}_picked_sequences.csv')


def main():
    args = get_args()
    set_constant_seeds()


    file_path =  args.file_name

    experiment_name = get_experiment_name(file_path)

    if is_preprocessed_already(experiment_name):
        print(f'Already preprocessed {experiment_name}')
    else:
        print(f'Preprocessing {experiment_name}')
        preprocess(file_path, experiment_name)


    if args.algorithm == 'FiSSC':
        paper_algorithm(args, experiment_name, file_path)
    elif args.algorithm == 'Greedy':
        greedy_algorithms(args, experiment_name, file_path)
    elif args.algorithm == 'MIS_ILP':
        mis_ilp_algorithm(args, experiment_name, file_path)
    elif args.algorithm == 'debug_ILP':
        debug_ilp(args, experiment_name, file_path)
    elif args.algorithm == 'preprocess_test':
        test_preprocess(file_path, experiment_name)
    elif args.algorithm == 'MIS_ILP_p1':
        mis_ilp_algorithm_p1(args, experiment_name, file_path)
    elif args.algorithm == 'MIS_ILP_p2':
        mis_ilp_algorithm_p2(args, experiment_name, file_path)
    elif args.algorithm == 'verify_solution':
        validate_fissc_solution(experiment_name)

    else:
        print('Invalid algorithm')




if __name__ == '__main__':
    main()
