
#!/usr/bin/env python3
import os, subprocess, glob, time, sys, re, psutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.cm import ScalarMappable

from Benchmarks.performance_analysis import create_table
from Benchmarks.visualization import create_plot
from Benchmarks.script_runner import run_script

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
                    : File size:
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
                    day_time, day_lines, day_size, day_peak_memory = 0, 0, 0, 0
                    languages = set()

                    # Execute all scripts for the day
                    for script_file in glob.glob(f"{day_path}/*"):
                        match = re.search(rf"{Year}Day(\d+)(?:_P\d+)?", os.path.basename(script_file))
                        script_day = int(match.group(1)) if match else None

                        if script_day == day_number:
                            result = run_script(script_file)
                            if result:
                                extension, line_count, file_size, elapsed_time, peak_memory = result
                                day_time += elapsed_time * 1000
                                day_lines += line_count
                                day_size  += file_size
                                day_peak_memory = max(day_peak_memory, peak_memory)  # Track highest memory usage
                                languages.add(extension[1:])  # Store language/extension without dot

                    # Collect results for this day
                    if day_time > 0:
                        languages_str = ", ".join(sorted(languages))
                        times_taken[day_number].append(day_time)  # Add this iteration's time
                        peak_memory_usage[day_number].append(day_peak_memory)
                        if day_number not in file_info:
                            file_info[day_number] = (f".{languages_str}", day_lines, day_size)

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