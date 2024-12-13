import os, subprocess, glob, time, sys, re, psutil
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.cm import ScalarMappable
matplotlib.use('Qt5Agg')  # Non-GUI backend

def generate_gradient_around_color(center_color, num_steps=10):
    """Create a gradient around the given center color."""
    center_rgb = mcolors.hex2color(center_color)
    lighter_colors = [tuple(min(1, c + i * 0.05) for c in center_rgb) for i in range(num_steps)]
    darker_colors = [tuple(max(0, c - i * 0.05) for c in center_rgb) for i in range(num_steps)]
    # Combine them to form a full gradient (darker -> center -> lighter)
    full_gradient = darker_colors[::-1] + [center_rgb] + lighter_colors
    return full_gradient[::-1]

def create_plot(df, challenge, Year, Iters, save_dir, center_color="#4CAF50", scale='linear'):
    """
    Create a plot for average times with dynamic scaling and annotations.

    Parameters:
        df (DataFrame): Input data with columns ['Day', 'Avg(ms)', 'STD(ms)', 'Lang', 'Lines', 'Avg(MB)'].
        challenge (str): Challenge name (e.g., 'Advent of Code').
        Year (int): Year of the challenge.
        Iters (int): Num of iterations.
        save_dir (str): save to directory
        center_color (str): Base color for the gradient (default: "#4CAF50").
        scale (str): Y-axis scaling ('linear' or 'log'). Default is 'linear'.

    Returns:
        dict: Computed statistics including total time, min/max times, average, and percentages.
    """
    # Remove the "Total" row (if it exists) to avoid plotting it
    df = df[df['Day'] != 'Total']

    # Convert the 'Day' column to numeric
    days = pd.to_numeric(df['Day'], errors='coerce')  # Convert days to numeric, coercing any errors to NaN
    avg_times = df[f'Avg(ms)'].tolist()  # Get the average times for each day
    std_devs = df[f'STD(ms)'].tolist()
    avg_mems = df[f'Avg(MB)'].tolist()  # Get the average memory usage for each day
    rel_memory = df['Memory %'].tolist()  # Percentage of total memory for each day

    # Handle the file info (Langs and Lines)
    file_info = dict(zip(df['Lang'], zip(df['Lang'], df['Lines'])))  # Create a dict of file info for Langs and Lines

    # Create a color gradient around the center color
    color_gradient = generate_gradient_around_color(center_color)
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_gradient", color_gradient)

    # Normalize the percentage values for color mapping
    total_time = np.sum(avg_times)  # Total time (sum of avg times)
    total_mem = np.sum(avg_mems)  # Total memory (sum of avg memory usage)
    norm = mcolors.Normalize(vmin=min(rel_memory), vmax=max(rel_memory))
    bar_colors = [cmap(norm(p)) for p in rel_memory]

    # Create the plot
    fig, ax = plt.subplots(figsize=(15.6, 15.6 * 9 / 16))
    bars = ax.bar(days, avg_times, color=bar_colors, zorder=3, alpha=0.95)

    # Annotate the bars with file info (extension and line count)
    for i, (bar, percentage) in enumerate(zip(bars, rel_memory)):
        label_y = bar.get_height()
        label_x = (bar.get_x() + bar.get_width() / 2)
        file_path = df['Lang'].iloc[i]  # Get the file extension
        file_size = df['Size(kB)'].iloc[i]  # Get the line count
        memory = df['Avg(MB)'].iloc[i]
        ax.annotate(f"({file_path} | {file_size:.2f} kB) \n PM = {memory:.1f} MB",
                    xy=(label_x, label_y),
                    xytext=(label_x - 0.3, label_y * 1.15),
                    arrowprops=dict(facecolor='black', arrowstyle='->'),
                    fontsize=7, color='black', rotation=90, zorder = 5)
    # Validate and apply dynamic scaling
    if scale not in ['linear', 'log']:
        raise ValueError("Invalid value for scale. Choose either 'linear' or 'log'.")

    ax.set_yscale(scale)  # Set y-axis scale based on user input

    # Set the y-axis limit dynamically
    if scale == 'linear':
        max_y_value = max(avg_times)
        ax.set_ylim(0, max_y_value * 1.425)
    elif scale == 'log':
        # Generate more tick points for the log scale
        min_y = max(min(avg_times) * 0.9, 1e-2)  # Adjusted min y value
        max_y = max(avg_times) * 3.2  # Adjusted max y value
        ax.set_ylim(min_y, max_y)

    # Highlight max and min points
    max_color = 'red'
    min_color = 'blue'
    max_idx = np.argmax(avg_times)  # Index of max average time
    min_idx = np.argmin(avg_times)  # Index of min average time
    max_day, max_time = days[max_idx], avg_times[max_idx]  # Day and value for max
    min_day, min_time = days[min_idx], avg_times[min_idx]  # Day and value for min

    # Highlight max and min bars by setting edge colors and linewidths
    bars[max_idx].set_edgecolor(max_color)  # Red edge for max
    bars[max_idx].set_linewidth(2)
    bars[min_idx].set_edgecolor(min_color)  # Blue edge for min
    bars[min_idx].set_linewidth(2)

    # Add markers for max and min points with labels
    ax.plot(max_day, max_time, '-', color = max_color, label=f"Max: {max_time/1000:.2f} s", markersize=8, zorder=5)
    ax.plot(min_day, min_time, '-', color = min_color, label=f"Min: {min_time/1000:.2f} s", markersize=8, zorder=5)

    # Add average and median lines
    average_time = np.mean(avg_times)  # Mean of the average times
    median_time = np.median(avg_times)  # Median of the average times
    ax.axhline(average_time, color='#008000', linestyle='-', label=f'Average: {average_time/1000:.2f} s')
    ax.axhline(median_time,  color='#800080', linestyle='-', label=f'Median: {median_time/1000:.2f} s')

    # Add error bars based on the standard deviation for each day
    ax.errorbar(days, avg_times, yerr=std_devs, fmt='none', color='#FFD700', capsize=3, zorder=4)

    # Customize x-axis and y-axis labels
    ax.set_xticks(days)
    ax.set_xticklabels([f'Day {int(day)}' for day in days], rotation=45, ha='right')  # Ensure days are displayed as integers
    ax.set_ylabel(f"({scale.capitalize()} Scale) Average Time (ms)", fontsize=14)
    ax.set_title(f'{challenge}: Year {Year}',
                    fontsize=21, fontweight='bold')

    # Add grid and legend
    ax.grid(visible=True, which='major', axis='y', linestyle='--', linewidth=0.8, alpha=0.8)
    ax.minorticks_on()
    ax.grid(visible=True, which='minor', axis='y', linestyle=':', linewidth=0.6, alpha=0.6)

    ax.legend(loc='upper left', bbox_to_anchor=(0, 1), fontsize=9,
                frameon=True, facecolor='white', edgecolor='black')

    # Add custom information to the legend (using proxy artists)
    custom_lines = [
        plt.Line2D([0], [0], color='white', label=f"Scale: {scale.capitalize()}"),
        plt.Line2D([0], [0], color='white', label=f"Iterations: {Iters}"),
        plt.Line2D([0], [0], color='white', label=f"Peak Memory (PM): {total_mem:.2f} MB"),
        plt.Line2D([0], [0], color='white', label=f"Avg Year Run Time: {total_time/1000:.2f} s"),
    ]

    # Existing legend items (e.g., for average, median, max, min)
    legend_items = ax.legend(loc='upper left', bbox_to_anchor=(0, 1), fontsize=7,
                            frameon=True, facecolor='white', edgecolor='black')

    # # Combine the custom lines and existing legend
    final_legend = ax.legend(handles=custom_lines + legend_items.legend_handles,
                            loc='upper left', bbox_to_anchor=(0, 1), fontsize=9,
                            frameon=True, facecolor='white', edgecolor='black',
                            ncol=2)

    # Re-add the updated legend to the plot
    ax.add_artist(final_legend)

    # Make the plot layout tight
    plt.tight_layout()

    # Add a colorbar for the relative percentage
    cbar = plt.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax)
    cbar.set_label(f'Relative Percentage of Total Peak Memory (%)', fontsize=12)

    # Save and show the plot
    plot_path = os.path.join(save_dir, f"{Year}_{scale.capitalize()}_plot.png")
    plt.savefig(plot_path, bbox_inches='tight')
    plt.show()

    print(f"Plot saved to {plot_path}")

    # Return computed statistics
    return {
        'total_time': total_time,
        'min_time': min_time,
        'max_time': max_time,
        'average_time': average_time,
        'median_time': median_time,
        'std_dev_time': np.std(avg_times),  # standard deviation for avg_times
        'percentages': rel_memory,
        'max_day': max_day,
        'min_day': min_day
    }
