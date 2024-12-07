# Challenge - 2024
# # Solved in {2024}
# Puzzle Link: https://challenge.com/event/2024/
# Solution by: [author]
# Brief: [Run all 2024 scripts]

#!/usr/bin/env python3
import os, subprocess, glob, time, sys, re, psutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.cm import ScalarMappable

def get_file_line_count(file_path):
    """Get the number of lines in a script file."""
    try:
        with open(file_path, "r") as file:
            return len(file.readlines())
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

def monitor_memory_usage(process):
    """Monitor the peak memory usage of a subprocess."""
    try:
        peak_memory = 0
        while process.poll() is None:  # While process is still running
            mem_info = psutil.Process(process.pid).memory_info()
            peak_memory = max(peak_memory, mem_info.rss)
            time.sleep(0.1)  # Poll at intervals
        return peak_memory / (1024 ** 2)  # Convert to MB
    except psutil.NoSuchProcess:
        return 0  # Process ended too quickly to monitor

def generate_gradient_around_color(center_color, num_steps=10):
    """Create a gradient around the given center color."""
    center_rgb = mcolors.hex2color(center_color)
    lighter_colors = [tuple(min(1, c + i * 0.05) for c in center_rgb) for i in range(num_steps)]
    darker_colors = [tuple(max(0, c - i * 0.05) for c in center_rgb) for i in range(num_steps)]
    # Combine them to form a full gradient (darker -> center -> lighter)
    full_gradient = darker_colors[::-1] + [center_rgb] + lighter_colors
    return full_gradient[::-1]

def run_script(file_path):
    """
    Executes a script based on its file extension and measures its execution time and peak memory usage.

    Parameters:
        file_path (str): Path to the script file to be executed.

    Returns:
        tuple: (file_extension, line_count, elapsed_time, peak_memory_usage) if successful, otherwise None.
    """
    _, extension = os.path.splitext(file_path)
    file_name = os.path.basename(file_path)

    try:
        # Ignore unsupported files
        if extension in ['.txt', '.png', '.exe']:
            return None
        if file_name.startswith("Alt"):
            print(f"Skipping script: {file_name} (starts with 'Alt')")
            return None
        else:
            print(f"Running script: {file_name}")

        start_time = time.time()

        process = None
        if extension == '.py':
            process = subprocess.Popen(['python', file_path], env={**os.environ, "SUPPRESS_PLOT": "1"})
        elif extension == '.c':
            executable = file_path.replace('.c', '')
            subprocess.run(['gcc', file_path, '-o', executable], check=True)
            process = subprocess.Popen([executable])
        elif extension == '.rb':
            process = subprocess.Popen(['ruby', file_path])
        elif extension == '.jl':
            process = subprocess.Popen(['julia', file_path])
        else:
            print(f"Unsupported file type for {file_name}. Skipping.")
            return None

        peak_memory = monitor_memory_usage(process)
        process.wait()  # Ensure the process has finished

        elapsed_time = time.time() - start_time
        print(f"Finished running {file_name} in {elapsed_time:.2f} seconds with peak memory usage {peak_memory:.2f} MB.")

        line_count = get_file_line_count(file_path)
        return extension, line_count, elapsed_time, peak_memory
    except subprocess.CalledProcessError as e:
        print(f"Error executing {file_name}: {e}")
        return None

def create_table(file_info, times_taken, peak_memory_usage, num_iterations, year):
    """
    Generates a table summarizing iterations and statistics for available days.
    Saves the table to a file and creates a DataFrame with the data.

    Parameters:
        file_info (dict): Contains programming language and line count for each day.
        times_taken (dict): Contains execution times for each day.
        peak_memory_usage (dict): Contains memory usage for each day.
        num_iterations (int): Number of iterations the tests ran.
        year (int): The year of the event.
    Returns:
        pandas.DataFrame: DataFrame containing the summary table data.
    """
    print("\nGenerating table...")

    # Initialize dictionaries for statistics
    avg_execution_times = {}
    std_dev_execution_times = {}
    avg_memory_usages = {}
    std_dev_memory_usages = {}

    # Calculate averages and standard deviations for execution times
    for day, times in times_taken.items():
        if times:
            avg_execution_times[day] = np.mean(times)
            std_dev_execution_times[day] = np.std(times)
        else:
            avg_execution_times[day] = 0
            std_dev_execution_times[day] = 0

    # Calculate averages and standard deviations for memory usage
    for day, memory_usages in peak_memory_usage.items():
        if memory_usages:
            avg_memory_usages[day] = np.mean(memory_usages)
            std_dev_memory_usages[day] = np.std(memory_usages)
        else:
            avg_memory_usages[day] = 0
            std_dev_memory_usages[day] = 0

    # Define table headers
    headers = [
        "Day", "Avg(s)", "STD(s)", "Time %",
        "Avg(MB)", "STD(MB)", "Memory%",
        "Lang", "Lines"
    ]
    row_format = "{:<7}" + "{:<10}" * (len(headers) - 1)

    # Initialize table content and DataFrame data
    table_lines = [row_format.format(*headers), "-" * (len(headers) * 15)]
    data_for_df = []

    # Totals and aggregates for the summary row
    total_time = sum(avg_execution_times.values())
    total_memory = sum(avg_memory_usages.values())
    total_lines_of_code = 0
    cumulative_time_percentage = 0
    cumulative_memory_percentage = 0
    cumulative_time_std = 0
    cumulative_memory_std = 0
    # Collect all average times for additional statistics
    all_avg_times = []

    # Populate table rows
    for day in sorted(times_taken.keys()):
        avg_time = avg_execution_times.get(day, 0)
        std_time = std_dev_execution_times.get(day, 0)
        cumulative_time_std += std_time
        avg_memory = avg_memory_usages.get(day, 0)
        std_memory = std_dev_memory_usages.get(day, 0)
        cumulative_memory_std += std_memory

        # Skip rows with no data
        if avg_time == 0 and avg_memory == 0:
            continue

        time_percentage = (avg_time / total_time * 100) if total_time > 0 else 0
        memory_percentage = (avg_memory / total_memory * 100) if total_memory > 0 else 0

        cumulative_time_percentage += time_percentage
        cumulative_memory_percentage += memory_percentage

        language, lines_of_code = file_info.get(day, ("N/A", 0))
        total_lines_of_code += lines_of_code

        # Add data to the DataFrame list
        data_for_df.append([
            day, avg_time, std_time, time_percentage,
            avg_memory, std_memory, memory_percentage,
            language, lines_of_code
        ])

        # Add data to the text table
        table_lines.append(row_format.format(
            f" {day} ", f"{avg_time:.2f}", f"{std_time:.2f}", f"{time_percentage:.2f}%",
            f"{avg_memory:.2f}", f"{std_memory:.2f}", f"{memory_percentage:.2f}%", 
            language, f"  {lines_of_code}  "
        ))

        # Track all average times for further statistics
        all_avg_times.append(avg_time)

    # Calculate additional statistics for execution times
    all_avg_times = np.array(all_avg_times)
    min_avg_time = np.min(all_avg_times) if all_avg_times.size > 0 else 0
    max_avg_time = np.max(all_avg_times) if all_avg_times.size > 0 else 0
    median_avg_time = np.median(all_avg_times) if all_avg_times.size > 0 else 0

    # Add a totals row
    table_lines.append("-" * (len(headers) * 15))
    table_lines.append(row_format.format(
        "Total", f"{total_time:.2f}", f"{cumulative_time_std:.2f}", f"{cumulative_time_percentage:.2f}%", 
        f"{total_memory:.2f}", f"{cumulative_memory_std:.2f}", f"{cumulative_memory_percentage:.2f}%", 
        "N/A", f"  {total_lines_of_code}"
    ))

    # Add additional info
    table_lines.append("\n")
    table_lines.append(f"Year: {year}, Iterations: {num_iterations}")

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data_for_df, columns=headers)

    # Add a totals row to the DataFrame
    df.loc[len(df)] = [
        "Total", total_time, cumulative_time_std, cumulative_time_percentage, 
        total_memory, cumulative_memory_std, cumulative_memory_percentage, 
        "N/A", total_lines_of_code
    ]
    print(df)
    return df, table_lines

def create_plot(df, challenge, Year, Iters, save_dir, center_color="#4CAF50", scale='linear'):
    """
    Create a plot for average times with dynamic scaling and annotations.

    Parameters:
        df (DataFrame): Input data with columns ['Day', 'Avg(s)', 'STD(s)', 'Lang', 'Lines', 'Avg(MB)'].
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
    avg_times = df[f'Avg(s)'].tolist()  # Get the average times for each day
    std_devs = df[f'STD(s)'].tolist()
    avg_mems = df[f'Avg(MB)'].tolist()  # Get the average memory usage for each day
    rel_memory = df['Memory%'].tolist()  # Percentage of total memory for each day

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
        line_count = df['Lines'].iloc[i]  # Get the line count
        memory = df['Avg(MB)'].iloc[i]
        ax.annotate(f"({file_path}) {line_count} lines \n ({memory:.1f} MB)",
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
    ax.plot(max_day, max_time, '-', color = max_color, label=f"Max ({max_time:.2f}s)", markersize=8, zorder=5)
    ax.plot(min_day, min_time, '-', color = min_color, label=f"Min ({min_time:.2f}s)", markersize=8, zorder=5)

    # Add average and median lines
    average_time = np.mean(avg_times)  # Mean of the average times
    median_time = np.median(avg_times)  # Median of the average times
    ax.axhline(average_time, color='#008000', linestyle='-', label=f'Average: {average_time:.2f}s')
    ax.axhline(median_time, color='#800080', linestyle='-', label=f'Median: {median_time:.2f}s')

    # Add error bars based on the standard deviation for each day
    ax.errorbar(days, avg_times, yerr=std_devs, fmt='none', color='#FFD700', capsize=3, zorder=4)

    # Customize x-axis and y-axis labels
    ax.set_xticks(days)
    ax.set_xticklabels([f'Day {int(day)}' for day in days], rotation=45, ha='right')  # Ensure days are displayed as integers
    ax.set_ylabel(f"({scale.capitalize()} Scale) Average Time (s)", fontsize=14)
    ax.set_title(f'{challenge}: Year {Year}',
                    fontsize=18, fontweight='bold')

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
        plt.Line2D([0], [0], color='white', label=f"Peak Memory Use: {total_mem:.2f} MB"),
        plt.Line2D([0], [0], color='white', label=f"Avg Year Run Time: {total_time:.2f}s"),
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

def execute_challenge_scripts(challenge, Year, days_to_run, base_dir, num_iterations=5, center_color="#4CAF50"):
    """
    Execute challenge scripts, aggregate performance statistics, and generate results.

    This function runs all scripts associated with a coding challenge (e.g., Advent of Code) for specified days 
    over multiple iterations. It measures execution time, counts lines of code, and tracks peak memory usage. 
    Results are aggregated and used to generate a summary table and performance plots.

    Parameters:
        challenge (str): The name of the challenge (e.g., "Advent of Code").
        Year (int): The year of the challenge (e.g., 2024).
        days_to_run (list): A list of integers specifying the days of the challenge to execute (e.g., [1, 2, 3]).
        base_dir (str): Base Directory where all challenge scripts are saved
        num_iterations (int): Number of iterations to execute each day's scripts (default is 5).
        center_color (str): The base color for gradients in plots (default is "#4CAF50").
    Returns:
        DataFrame: A Pandas DataFrame containing aggregated results, including:
                    : Day numbers.
                    : Average execution times.
                    : Standard deviations.
                    : Peak memory usage.
                    : Line counts.
                    : Languages used.
    """
    print(f"\n{challenge} - {Year}")
    print(f"Running scripts for days: {min(days_to_run)} to {max(days_to_run)} over {num_iterations} iterations.")

    # repo_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isdir(base_dir):
        print(f"Directory '{base_dir}' does not exist.")
        return

    # Data structures for storing results
    times_taken = {day: [] for day in days_to_run}  # Store times for each day across iterations
    file_info = {}  # Store script info for each day
    peak_memory_usage = {day: [] for day in days_to_run}  # Store peak memory usage for each day

    # Loop through iterations
    for iteration in range(num_iterations):
        print(f"\nIteration {iteration + 1}/{num_iterations}...")

        for day_dir in os.listdir(base_dir):
            day_path = os.path.join(base_dir, day_dir)
            if os.path.isdir(day_path) and day_dir.isdigit():
                day_number = int(day_dir)
                if day_number in days_to_run:
                    print(f"\nProcessing Day {day_number}...")
                    day_time, day_lines, day_peak_memory = 0, 0, 0
                    languages = set()

                    # Execute all scripts for the day
                    for script_file in glob.glob(f"{day_path}/*"):
                        match = re.search(rf"{Year}Day(\d+)(?:_P\d+)?", os.path.basename(script_file))
                        script_day = int(match.group(1)) if match else None

                        if script_day == day_number:
                            result = run_script(script_file)
                            if result:
                                extension, line_count, elapsed_time, peak_memory = result
                                day_time += elapsed_time
                                day_lines += line_count
                                day_peak_memory = max(day_peak_memory, peak_memory)  # Track highest memory usage
                                languages.add(extension[1:])  # Store language/extension without dot

                    # Collect results for this day
                    if day_time > 0:
                        languages_str = ", ".join(sorted(languages))
                        times_taken[day_number].append(day_time)  # Add this iteration's time
                        peak_memory_usage[day_number].append(day_peak_memory)
                        if day_number not in file_info:
                            file_info[day_number] = (f".{languages_str}", day_lines)

    # Use averaged times for the table and plot
    run_df, table_txt = create_table(file_info, times_taken, peak_memory_usage, num_iterations, Year)

    # Save the table to a text file
    output_file = os.path.join(base_dir, f"{Year}_Run_Summary.txt")
    with open(output_file, 'w') as f:
        for line in table_txt:
            f.write(line + "\n")
    print(f"Summary saved to {output_file}")

    # Create plots
    create_plot(run_df, challenge, Year, num_iterations, base_dir, center_color, scale='linear')
    create_plot(run_df, challenge, Year, num_iterations, base_dir, center_color, scale='log')

    print(f"\nTotal script execution time over {num_iterations} iterations saved to table and plotted.")

    return run_df

if __name__ == "__main__":
    Year = 2024
    Challenge = 'Challenge'
    days_to_run = range(1, 26)
    color_2024 = "#FFA500"
    num_iterations = 3  # Number of iterations for benchmarking

    repo_dir = os.path.dirname(os.path.abspath(__file__))
    file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    base_dir = os.path.abspath(os.path.join(os.getcwd(), f"{Year}"))
    script_dir = os.path.dirname(os.path.abspath(__file__))
    selected_dir = file_dir

    run_2024 = execute_challenge_scripts(Challenge, Year, days_to_run, selected_dir, num_iterations, color_2024)