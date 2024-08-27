import numpy as np
#from scripts.utils import *
import random

def get_known_sequences(sequences):
    # return all sequences without an X (A or G)
    return [seq for seq in sequences if 'X' not in seq]


def sequences_covers(sequence, other_sequence):
    """
    Returns true if other_sequence covers sequence
    if same character -> good
    if X -> covered by A or G
    """
    return all(
        seq == o_seq or (seq == 'X' and o_seq in 'AG')
        for seq, o_seq in zip(sequence, other_sequence)
    )
def sequences_covers_wildcards(sequence, other_sequence):
    """
    Returns true if other_sequence covers sequence
    if same character -> good
    if X -> covered by A or G
    """
    return all(
        seq == o_seq or (seq == 'X' and o_seq in 'AG')
        for seq, o_seq in zip(sequence, other_sequence)
    )

def get_sequences_not_covered(sequences, covering_sequences):

    print("Finding uncovered sequences")
    uncovered_seqs = []
    n_uncovered = 0
    n_covered = 0

    for i, seq in enumerate(sequences):
        if i % 100 == 0:
            print(f"Checking sequence {i}/{len(sequences)}, {n_covered} covered, {n_uncovered} uncovered")
        for cover in covering_sequences:
            if sequences_covers(seq, cover):
                n_covered += 1
                break
        else:
            uncovered_seqs.append(seq)
            n_uncovered += 1
    #clear_cell()
    return uncovered_seqs


def show_position_freq(sequences):
    # out of all covered check the frequency of each letter per position
    freqs = np.zeros((len(sequences[0]), 3))
    for seq in sequences:
        for i, letter in enumerate(seq):
            if letter == 'A':
                freqs[i, 0] += 1
            elif letter == 'G':
                freqs[i, 1] += 1
            elif letter == 'X':
                freqs[i, 2] += 1

    # show
    for i, freq in enumerate(freqs):
        print(f'Position {i}: {freq}')



def do_sequences_clash(seq1, seq2):
    return any(l1 != l2 and l1 != 'X' and l2 != 'X' for l1, l2 in zip(seq1, seq2))


def get_only_possible_assignments(sequences, up_to_k=6):
    """
    Returns sequences that only have 1 possible assignment
    """
    must_have_assignments_overall = []
    for k in range(1, up_to_k+1):
        print(f"Checking for k={k}")
        all_sequence_with_k_X = get_sequences_with_k_Xs(sequences,k)
        must_have_assignments_k_X = find_unique_X_assignments(all_sequence_with_k_X)
        must_have_assignments_overall.extend(must_have_assignments_k_X)

    return must_have_assignments_overall

def get_clashing_non_clashing(sequences):
    clashing_sequences = []
    non_clashing_sequences = []
    for i, seq1 in enumerate(sequences):
        is_clashing = True
        if i % 100 == 0:
            print(f"Checking sequence {i}/{len(sequences)}")
            
        for seq2 in sequences:
            if seq1 == seq2:
                continue
            if not do_sequences_clash(seq1, seq2):
                is_clashing = False
                non_clashing_sequences.append(seq1)
                break
        if is_clashing:
            clashing_sequences.append(seq1)
    #clear_cell()
    return clashing_sequences, non_clashing_sequences



def less_specific(seq1, seq2):
    """
    Returns True if seq1 is less specific than seq2
    """
    return all(l1 == l2 or l1 == 'X' for l1, l2 in zip(seq1, seq2))



def get_more_specific_sequences(sequences):
    if len(sequences) == 0:
        return [], []
    less_specific_sequences = set()

    # order non_clashing_sequences by number of X
    sequences = sorted(sequences, key=lambda x: x.count('X'), reverse=True)
    len_sequences = len(sequences)

    max_X = sequences[0].count('X')
    min_x = sequences[-1].count('X')

    first_count_apperance = {}
    for x_count in range(max_X+1):
        for i, seq in enumerate(sequences):
            if seq.count('X') == x_count:
                break
        first_count_apperance[x_count] = i

    first_count_apperance[min_x-1] = len(sequences)

    print(first_count_apperance)

    for i, seq in enumerate(sequences):
        x_count = seq.count('X')
        if i % 100 == 0:
            print(f"Checking sequence {i}/{len(sequences)}")
            print(f"Number of less specific sequences: {len(less_specific_sequences)}")
        min_range = first_count_apperance[x_count-1]
        for j in range (min_range, len_sequences):
            seq2 = sequences[j]
            if less_specific(seq, seq2):
                less_specific_sequences.add(seq)
                break


    # get the more specific sequences
    more_specific_sequences = set(sequences) - less_specific_sequences

    more_specific_sequences = list(more_specific_sequences)
    less_specific_sequences = list(less_specific_sequences)
    #clear_cell()
    return more_specific_sequences, less_specific_sequences




########################## PART B ############################


# gets all the sequences with k X's:
def get_sequences_with_k_Xs(sequences, k):
    return [seq for seq in sequences if seq.count('X') == k]


def generate_all_possible_sequences(k):
    return [''.join(seq) for seq in product('GA', repeat=k)]

from itertools import product

def find_unique_X_assignments(sequences_with_k_X):
    must_have_assignments = []
    for sequence in sequences_with_k_X:
        possible_assignments = generate_all_possible_sequences(sequence.count('X'))
        #print(possible_assignments)
        valid_assignments = []
        for assignment in possible_assignments:
            temp_seq = sequence
            #print(len(temp_seq), len(assignment))
            for replacement in assignment:
                temp_seq = temp_seq.replace('X', replacement, 1)
                #(temp_seq)
            for other_seq in sequences_with_k_X:
                if other_seq == sequence:
                    continue
                if not do_sequences_clash(temp_seq, other_seq):
                    valid_assignments.append(temp_seq)
                    break
        if len(valid_assignments) == 1:
            must_have_assignments.append(valid_assignments[0])
    return must_have_assignments


def find_all_occurrences(string, character):
    return [i for i, char in enumerate(string) if char == character]


def get_neighbores(sequence, all_sequences):
    return [seq for seq in all_sequences if not do_sequences_clash(seq, sequence)]


def merge_sequences(seq1, seq2):
    # the same as seq1 but every X is replaced by the corresponding letter in seq2
    return ''.join(l1 if l1 != 'X' else l2 for l1, l2 in zip(seq1, seq2))

def sequence_to_more_specific(sequence, all_sequences):
    x_positions = find_all_occurrences(sequence, 'X')
    #print(x_count)
    for x_pos in x_positions:

        neighbors = get_neighbores(sequence, all_sequences)

        if all(seq[x_pos] == 'G' for seq in neighbors):
            sequence = sequence[:x_pos] + 'G' + sequence[x_pos+1:]
            continue
        if all(seq[x_pos] == 'A' for seq in neighbors):
            sequence = sequence[:x_pos] + 'A' + sequence[x_pos+1:]
            continue

    return sequence



def make_sequences_specific(sequences):
    for i, sequence in enumerate(sequences):
        if i % 10 == 0:
            print(f"Sequence {i} out of {len(sequences)}")
        sequences[i] = sequence_to_more_specific(sequence, sequences)

    return sequences

def random_assignment(sequence):
    return ''.join(random.choice('GA') if l == 'X' else l for l in sequence)

def concensous_assignment(sequences, concensous_string):
    return ''.join(l if l != 'X' else c for l, c in zip(sequences, concensous_string))
