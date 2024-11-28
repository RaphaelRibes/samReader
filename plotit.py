import numpy as np
import matplotlib.pyplot as plt

def plot_depth(depth):
    """
    Plot the depth of the reads in a PDF file.

    Args:
        depth (np.array): A numpy array containing the depth of the reads.
    """
    # Truncate the depth array to a length divisible by 100
    depth = depth[:len(depth) - (len(depth) % 100)]

    # Compute the original positions in the sequence
    step = len(depth) // 100

    classes = [depth[i * step:(i + 1) * step] for i in range(100)]
    class_means = np.array([np.mean(cls) for cls in classes])

    # Reshape and compute the means and quartiles
    truncated_array = depth.reshape(-1, step)
    sampled_array = np.mean(truncated_array, axis=1)
    first_quartile = np.percentile(truncated_array, 25, axis=1)
    third_quartile = np.percentile(truncated_array, 75, axis=1)
    # std = np.std(truncated_array, axis=1)

    # Plot the data
    plt.figure(figsize=(10, 5))
    plt.plot(sampled_array)
    plt.fill_between(np.arange(len(sampled_array)), first_quartile, third_quartile, alpha=0.2)
    # plt.bar(range(1, 101), class_means, yerr=std)  # Une barre par classe

    # Adjust x-ticks to reflect original positions
    # Define ticks and labels
    num_ticks = 10  # Adjust the number of ticks you want
    ticks = np.linspace(0, len(sampled_array) - 1, num_ticks, dtype=int)
    tick_labels = np.linspace(0, len(depth) - 1, num_ticks, dtype=int)  # Match to original positions

    plt.xticks(ticks=ticks, labels=tick_labels, rotation=45)  # Optional rotation for better readability

    # Draw the mean depth
    plt.axhline(np.mean(sampled_array), color='red', linestyle='--', label='Mean depth')
    plt.annotate(f'    {np.mean(sampled_array):.2f}\nmean depth', (101, np.mean(sampled_array)), color='red', ha="left",
                 va="center")

    plt.ylabel("Depth")
    plt.xlabel("Position")

    # plt.ylim(0)
    plt.xlim(0, 101)

    # remove top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    plt.savefig("temp/chromosome.png")
    plt.close()
