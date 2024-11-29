import numpy as np
import matplotlib.pyplot as plt
import os, shutil

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