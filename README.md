
# FiSSC

This repository contains the implementation of FiSSC, a tool designed to identify the smallest sequence cover of ambiguous reads. It accompanies the paper titled "FiSSC: Finding Smallest Sequence Covers to Sets of Degenerate Reads with Applications to RNA Editing."


## Requirements

The tool has been tested with the following configuration on a Linux machine:
- Python 3.9.18
- GurobiPy 11.0.2
- NetworkX 3.2.1
- NumPy 1.26.4
- Pandas 2.1.2

 
## Setting Up the Tool
First, create a file named `gurobi.json` containing the details for the Gurobi license.

```json
{
  "WLSACCESSID": "XXXXX",
  "WLSSECRET": "XXXXX",
  "LICENSEID": 12345
}
```


## Running the Tool

Ensure that the zipped FASTA files are placed in the `data` folder. The files should follow the format of the example file `example.fa.gz`.

### Running the FiSSC Algorithm

To execute the FiSSC algorithm, use the following command:

```bash
python ./tool.py --file_name <file-name> --ILP_time_restriction_in_minutes <minutes> --threads <thread_count> [--do_logs]
```

- **file_name**: Only include the name of the file, without a path to the `data` folder.
- **ILP_time_restriction_in_minutes**: Specify an integer to set the time limit (in minutes) for the ILP solver per connected component in the read graph, default is 4 hours.
- **threads**: Define the number of threads available for the ILP solver.
- **--do_logs** (optional): Generates a CSV log file for the filtering process.

Example command:
```bash
python ./tool.py --file_name example.fa.gz --ILP_time_restriction_in_minutes 240 --threads 64 --do_logs
```


The tool produces the following files in the `output` folder:
1. A `*{name}_consensus.txt` file containing the constant and degenerate positions in all the sequences.
2. A `*{name}_picked_sequences.csv` file containing all the sequences picked by either the filtering step or the ILP solver.

[comment]: <> (Add contact in the final submission)

### Running other Algorithms

To execute the other algorithms, use the following command:

```bash
python ./tool.py --algorithm <algorithm> --file_name <file-name> 
```

The available options are: 
- FiSSC (default)
- Greedy
- MIS_ILP

'Greedy' produces both an upper bound for the sequence cover size (using greedy min-clique cover) and a lower bound (using greedy MIS). The results are then saved in `output/{name}_greedy_results.txt`.

Example command:
```bash
python ./tool.py --algorithm Greedy --file_name example.fa.gz 
```


'MIS_ILP' produces a lower bound using a solution to MIS using ILP. The results are then saved in `output/{name}_mis_ilp_results.txt`. You can use `ILP_time_restriction_in_minutes` to restrict the running time of the ILP solver, default is 4 hours.

Example command:
```bash
python ./tool.py --algorithm MIS_ILP --file_name example.fa.gz --ILP_time_restriction_in_minutes 1440 
```
