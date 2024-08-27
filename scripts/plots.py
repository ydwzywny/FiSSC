import numpy as np
def plot_x_hist(sequences):
    # plot the number of X per sequence
    n_X = [seq.count('X') for seq in sequences]
    max_X = max(n_X)

    import matplotlib.pyplot as plt
    plt.hist(n_X, bins=range(0, max_X+1))
    plt.xlabel('Number of X')
    plt.ylabel('Number of sequences')
    plt.title('Number of X per sequence')
    plt.show()


def get_x_stats(sequences):
    average_number_of_x = np.mean(([seq.count('X') for seq in sequences]))
    total_number_of_x = sum([seq.count('X') for seq in sequences])
    print(f'Average number of X: {average_number_of_x}')
    print(f'Total number of X: {total_number_of_x}')