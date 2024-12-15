import numpy as np
import matplotlib.pyplot as plt
import os, shutil

def plot_depth_mapq(depth: np.array,
                    mapq:list[(int, int)],
                    bins=100,
                    depth_median=True,
                    mapq_median=True,
                    n_ticks=10):
    """
    Plot the depth and mapq of the reads.

    Args:
        :param mapq: A list of tuples containing the position and the MAPQ score.
        :param depth: A numpy array containing the depth of the reads.
        :param mapq_median: A boolean indicating whether to use the median of the MAPQ scores.
        :param depth_median: A boolean indicating whether to use the median of the depth.
        :param bins: The number of bins to divide the data into.
    """

    # Remove the zeros at the beginning and the end of the arrays
    depth_start_index = np.argmax(depth != 0)  # First non-zero index
    depth_end_index = len(depth) - np.argmax(depth[::-1] != 0)  # Last non-zero index
    depth = depth[depth_start_index:depth_end_index]  # Remove the zeros at the beginning and the end

    mapq_start_index = np.argmax(mapq != 0)  # First non-zero index
    mapq_end_index = len(mapq) - np.argmax(mapq[::-1] != 0)  # Last non-zero index
    mapq = mapq[mapq_start_index:mapq_end_index]  # Remove the zeros at the beginning and the end

    min_index = min(depth_start_index, mapq_start_index)
    max_index = max(depth_end_index, mapq_end_index)

    # Divide the depth into bins
    ls_depth = np.linspace(0, len(depth), bins + 1, dtype=np.int64)
    ls_mapq = np.linspace(0, len(mapq), bins + 1, dtype=np.int64)

    classed_depth = [depth[ls_depth[i]:ls_depth[i + 1]] for i in range(bins)]  # Divide the depth into classes
    classed_mapq = [mapq[ls_mapq[i]:ls_mapq[i + 1]] for i in range(bins)]

    # I know this is not pretty, but at least it's clear what's happening
    if depth_median:
        sampled_depth = np.array([np.median(cd) if len(cd) > 0 else np.nan for cd in classed_depth])
        depth_lower_limit = np.array([np.percentile(cd, 25) if len(cd) > 0 else np.nan  for cd in classed_depth])
        depth_upper_limit = np.array([np.percentile(cd, 75) if len(cd) > 0 else np.nan  for cd in classed_depth])
    else:
        sampled_depth = np.array([np.mean(cd) if len(cd) > 0 else np.nan for cd in classed_depth])
        depth_lower_limit = np.array([sampled_depth[n]-np.std(cd) if len(cd) > 0 else np.nan for n, cd in enumerate(classed_depth)])
        depth_upper_limit = np.array([sampled_depth[n]+np.std(cd) if len(cd) > 0 else np.nan for n, cd in enumerate(classed_depth)])

    if mapq_median:
        sampled_mapq = np.array([np.median(cm) if len(cm) > 0 else np.nan for cm in classed_mapq])
        mapq_lower_limit = np.array([np.percentile(cm, 25) if len(cm) > 0 else np.nan for cm in classed_mapq])
        mapq_upper_limit = np.array([np.percentile(cm, 75) if len(cm) > 0 else np.nan for cm in classed_mapq])
    else:
        sampled_mapq = np.array([np.mean(cm) if len(cm) > 0 else np.nan for cm in classed_mapq])
        mapq_lower_limit = np.array([sampled_mapq[n]-np.std(cm) if len(cm) > 0 else np.nan for n, cm in enumerate(classed_mapq)])
        mapq_upper_limit = np.array([sampled_mapq[n]+np.std(cm) if len(cm) > 0 else np.nan for n, cm in enumerate(classed_mapq)])
    # The interpolation doesn't happen all the time, only when some values are missing
    # It's the limitation of this graph, it cannot be precise base-per-base without being confusing and so it has to be interpolated

    # Plot the depth and mapq
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()  # Share the same x-axis

    # Plot the depth
    ax1.plot(sampled_depth, label='Mean depth', color='tab:blue')
    ax1.fill_between(np.arange(0, len(classed_depth)), depth_lower_limit, depth_upper_limit, alpha=0.3, label='Interquartile range', color='tab:blue')

    # Set the labels and limits
    ax1.set_xlim(0, bins-1)
    ax1.set_ylim(0)
    ax1.set_ylabel("Depth", color='tab:blue')
    ax1.spines['left'].set_color('tab:blue')
    ax1.set_xlabel("Position")
    ax1.tick_params(colors='tab:blue', axis='y')

    # Plot the mapq
    ax2.plot(sampled_mapq, color='tab:orange', label='MAPQ')
    ax2.fill_between(np.arange(0, len(classed_mapq)), mapq_lower_limit, mapq_upper_limit, alpha=0.3, color='tab:orange')
    ax2.set_ylabel('MAPQ', color='tab:orange')
    ax2.spines['right'].set_color('tab:orange')

    # Set the labels and limits
    ax2.set_xlim(0, bins-1)
    ax2.set_ylim(0)
    ax2.tick_params(colors='tab:orange', axis='y')

    # Adjust x-ticks to reflect original positions
    ticks = np.linspace(0, len(classed_depth) - 1, n_ticks, dtype=int)
    tick_labels = np.linspace(min_index, max_index, n_ticks, dtype=int)  # Match to original positions

    ax1.set_xticks(ticks)
    ax1.set_xticklabels([format_size(tick_label) for tick_label in tick_labels], rotation=45)

    # Draw the mean/median depth
    if depth_median:
        ax1.axhline(np.median(depth), color='tab:blue', linestyle='--', label=f'Median depth')
    else:
        ax1.axhline(np.mean(depth), color='tab:blue', linestyle='--', label='Mean depth')

    if np.mean(depth) <= 1:
        ax1.annotate(f'{np.mean(depth):.2f}\n{'Median' if depth_median else 'Mean'}  depth',
                     (0.5, np.mean(depth)),
                     color='tab:blue',
                     va="bottom")
    else:
        ax1.annotate(f'{np.mean(depth):.2f}\n{'Median' if depth_median else 'Mean'} ', (0.5, np.mean(depth)-1),
                     color='tab:blue',
                     va="top")

    # Remove top and right spines for ax1
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)

    plt.tight_layout()  # Adjust the layout

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
                    sizes.append(len(f.readlines())//2)  # Divide by 2 to get the number of reads

            # sizes = [only_unmapped, only_mapped, only_partially_mapped]
            ratio.append((sizes[1] + 0.5*sizes[2]) / sum(sizes))

    plt.figure(figsize=(10, 5))
    plt.bar(names, ratio)
    plt.ylabel("Ratio of mapped reads/total")

    plt.savefig("temp/mapping_ratio.png", dpi=300)
    plt.close()

def format_size(size: int) -> str:
    """
    Format the size of the file in a human-readable format.

    Args:
        size (int): The size of the file in bytes.

    Returns:
        str: The size of the file in a human-readable format.
    """
    for unit in ['bp', 'Kbp', 'Mbp', 'Gbp', 'Tbp']:
        if size <= 1000:
            return f"{size:.2f} {unit}"
        size /= 1000


if __name__ == "__main__":
    os.makedirs(os.path.join(os.getcwd(), "temp"), exist_ok=True)
    plot_mapping_ratio("mapping_results")
    shutil.rmtree(os.path.join(os.getcwd(), "temp"))