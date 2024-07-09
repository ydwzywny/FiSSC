
import numpy as np
import pandas as pd
import numpy as np
import pandas as pd
import random
import gzip


def set_constant_seeds():
    np.random.seed(42)
    random.seed(42)

def get_experiment_name(file_path):
    with gzip.open(file_path, "rt") as handle:
        experiment_name = handle.readline().split()[-1]
        return experiment_name