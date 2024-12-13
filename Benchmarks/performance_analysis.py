
import numpy as np
import pandas as pd

def create_table(file_info, times_taken, peak_memory_usage, num_iterations, year):
    """
    Generates a table summarizing iterations and statistics for available days.
    Saves the table to a file and creates a DataFrame with the data.

    Parameters:
        file_info (dict): Contains programming language, line count and file size for each day.
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
        "Day", "Avg(ms)", "STD(ms)", "Time %",
        "Avg(MB)", "STD(MB)", "Memory %",
        "Lang", "Size(kB)", "Lines"
    ]
    row_format = "{:<7}" + "{:<12}" + "{:<10}" * (len(headers) - 2)

    # Initialize table content and DataFrame data
    table_lines = [row_format.format(*headers), "-" * (len(headers) * 10)]
    data_for_df = []

    # Totals and aggregates for the summary row
    total_time = sum(avg_execution_times.values())
    total_memory = sum(avg_memory_usages.values())
    total_lines_of_code = 0
    all_script_sizes = 0
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

        language, lines_of_code, file_size = file_info.get(day, ("N/A", 0))
        total_lines_of_code += lines_of_code
        all_script_sizes += file_size

        # Add data to the DataFrame list
        data_for_df.append([
            day, avg_time, std_time, time_percentage,
            avg_memory, std_memory, memory_percentage,
            language, file_size, lines_of_code
        ])

        # Add data to the text table
        table_lines.append(row_format.format(
            f" {day} ", f"{avg_time:.2f}", f" {std_time:.2f}", f"{time_percentage:.2f}%",
            f" {avg_memory:.2f}", f" {std_memory:.2f}", f"{memory_percentage:.2f}%",
            language, f" {file_size:.2f} ", f" {lines_of_code} "
        ))

        # Track all average times for further statistics
        all_avg_times.append(avg_time)

    # Calculate additional statistics for execution times
    all_avg_times = np.array(all_avg_times)
    min_avg_time = np.min(all_avg_times) if all_avg_times.size > 0 else 0
    max_avg_time = np.max(all_avg_times) if all_avg_times.size > 0 else 0
    median_avg_time = np.median(all_avg_times) if all_avg_times.size > 0 else 0

    # Add a totals row
    table_lines.append("-" * (len(headers) * 10))
    table_lines.append(row_format.format(
        "Total", f"{total_time:.2f}", f"{cumulative_time_std:.2f}", f"{cumulative_time_percentage:.2f}%", 
        f"{total_memory:.2f}", f" {cumulative_memory_std:.2f}", f"{cumulative_memory_percentage:.2f}%", 
        " N/A", f" {all_script_sizes:.2f}", f"{total_lines_of_code}"
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
        "N/A", all_script_sizes, total_lines_of_code
    ]
    print(df)
    return df, table_lines