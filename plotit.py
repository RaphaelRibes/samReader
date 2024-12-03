import numpy as np
import matplotlib.pyplot as plt
import os, shutil

def plot_depth(depth, bins=100):
    """
    Plot the depth of the reads in a PDF file.

    Args:
        depth (np.array): A numpy array containing the depth of the reads.
        :param bins: The number of bins to divide the data into.
    """
    ls = np.linspace(0, len(depth), bins+1, dtype=np.int64)  # Get the positions of the 100 classes
    classed_array = [np.array(depth[ls[i]:ls[i + 1]]) for i in range(bins)]  # Create a list of arrays

    sampled_array = np.array([np.mean(classed_array[i]) for i in range(bins)])
    first_quartile = np.array([np.percentile(classed_array[i], 25) for i in range(bins)])
    third_quartile = np.array([np.percentile(classed_array[i], 75) for i in range(bins)])

    # Plot the data
    plt.figure(figsize=(10, 5))
    plt.plot(sampled_array)
    plt.fill_between(np.arange(len(sampled_array)), first_quartile, third_quartile, alpha=0.2)

    # Adjust x-ticks to reflect original positions
    # Define ticks and labels
    num_ticks = 10  # Adjust the number of ticks you want
    ticks = np.linspace(0, len(sampled_array) - 1, num_ticks, dtype=int)
    tick_labels = np.linspace(0, len(depth) - 1, num_ticks, dtype=int)  # Match to original positions

    plt.xticks(ticks=ticks, labels=tick_labels, rotation=45)  # Optional rotation for better readability

    # Draw the mean depth
    plt.axhline(np.mean(sampled_array), color='red', linestyle='--', label='Mean depth')
    plt.annotate(f'    {np.mean(sampled_array):.2f}\nmean depth', (bins+1, np.mean(sampled_array)), color='red', ha="left",
                 va="center")

    plt.ylabel("Depth")
    plt.xlabel("Position")

    # plt.ylim(0)
    plt.xlim(0, bins+1)

    # remove top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    plt.savefig("temp/chromosome.png", dpi=300)
    plt.close()

def plot_mapping_ratio(results_dir: str):
    # iterate over the file that end with .fasta and count the numbers of lines
    ratio = []
    names = []
    for file in os.listdir(results_dir):
        file_path = os.path.join(results_dir, file)
        if os.path.isdir(file_path):
            sizes = []
            names.append(file)
            for subfile in os.listdir(file_path):
                subfile_path = os.path.join(file_path, subfile)
                with open(subfile_path, "r") as f:
                    sizes.append(len(f.readlines())//2)

            # sizes = [only_unmapped, only_mapped, only_partially_mapped]
            ratio.append((sizes[1] + 0.5+sizes[2]) / sum(sizes))

    plt.figure(figsize=(10, 5))
    plt.bar(names, ratio)
    plt.ylabel("Ratio of mapped reads/total")

    plt.savefig("temp/mapping_ratio.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    os.makedirs(os.path.join(os.getcwd(), "temp"), exist_ok=True)
    plot_mapping_ratio("mapping_results")
    shutil.rmtree(os.path.join(os.getcwd(), "temp"))