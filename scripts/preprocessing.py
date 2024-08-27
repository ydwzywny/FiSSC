import os
import numpy as np
import pandas as pd
import gzip
from Bio import SeqIO



def fasta_to_dataframe_gz(fasta_gz_path):
    """
    Converts a gzip-compressed FASTA file into a pandas DataFrame.
    
    Parameters:
    fasta_gz_path (str): Path to the gzip-compressed FASTA file (.fa.gz).

    Returns:
    pd.DataFrame: DataFrame containing two columns: 'ID' and 'Sequence'.
    """
    # Open the gzip-compressed FASTA file
    with gzip.open(fasta_gz_path, "rt") as handle:
        # Parse the FASTA file
        records = SeqIO.parse(handle, "fasta")
        
        # Extract data
        data = [(record.id, str(record.seq)) for record in records]
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=['ID', 'Sequence'])
    return df



def unique_sequences(df):
    """
    Extracts unique sequences from the 'Sequence' column of a DataFrame.

    Parameters:
    df (pd.DataFrame): The input DataFrame with a 'Sequence' column.

    Returns:
    pd.DataFrame: A DataFrame containing only unique values from the 'Sequence' column.
    """
    # Select the 'Sequence' column and drop duplicates
    unique_df = df[['Sequence']].drop_duplicates()

    return unique_df


def generate_concensous_and_datasets(df):
    sequences=  df['Sequence'].values
    length = len(sequences[0])
    seqs_df = pd.DataFrame(sequences)
    concensous = []
    for i in range(length):
        if i % 10 == 0:
            print(f"Checking position {i}/{length}")
        seqs_df = pd.DataFrame(sequences, columns=['Sequence'])
        seqs_df['Sequence'] = seqs_df['Sequence'].map(lambda x: x[i])

        if len(seqs_df['Sequence'].unique()) == 1:
            unique = seqs_df['Sequence'].unique()[0]
            concensous.append((i, unique))

    print(f"Concensous positions: {len(concensous)}")
    print(f"Variants: {length - len(concensous)}")

    concensous_string = ''

    # print the concensous positions
    positions = [x[0] for x in concensous]
    chars = [x[1] for x in concensous]

    for i in range(length):
        if i in positions:
            concensous_string += chars[positions.index(i)]
        else:
            concensous_string += 'X'

    variable_positions = [i for i in range(length) if i not in positions]

    df_only_variables  = df.copy()
    df_only_variables['Sequence'] = df_only_variables['Sequence'].apply(lambda x: ''.join(x[i] for i in variable_positions))

    return concensous_string, df_only_variables



def preprocess(experiment_file_path, experiment_name):
    
    df = fasta_to_dataframe_gz(experiment_file_path)
    len_df = len(df['Sequence'])
    print(f'number of sequences in {experiment_name}: {len_df}')
    
    df = unique_sequences(df)
    concensous_string, df_only_variables = generate_concensous_and_datasets(df)

    # save the variable_positions to csv file
    df_only_variables.to_csv(f'data/{experiment_name}.csv')

    # make sure the output directory exists
    if not os.path.exists('output'):
        os.makedirs('output')

    # save concensous string to text file
    with open(f'output/{experiment_name}_concensous.txt', "w") as text_file:
        text_file.write(concensous_string)


def is_preprocessed_already(experiment_name):
    return os.path.exists(f'data/{experiment_name}.csv') and os.path.exists(f'output/{experiment_name}_concensous.txt')
