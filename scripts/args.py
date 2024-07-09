import argparse



def get_args():
    parser = argparse.ArgumentParser(description='Process some sequences.')
    parser.add_argument('--algorithm', type=str, default='FiSSC', help='Algorithm/s to use. Options: paper, greedy, mis_ilp', choices=['FiSSC', 'Greedy', 'MIS_ILP', 'debug_ILP', 'preprocess_test','MIS_ILP_p1','MIS_ILP_p2', 'verify_solution'])
    parser.add_argument('--file_name', type=str, required=True, help='Name of the input file')
    parser.add_argument('--do_logs', action='store_true', help='Enable extensive logging')
    parser.add_argument('--ILP_time_restriction_in_minutes', type=int, default=240, help='ILP time restriction in minutes')
    parser.add_argument('--threads', type=int, default=64, help='Number of threads to use for ILP')

    args = parser.parse_args()
    return args
