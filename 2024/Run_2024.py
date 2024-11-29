# Challenge - 2024
# # Solved in {2024}
# Puzzle Link: https://challenge.com/event/2024/
# Solution by: [author]
# Brief: [Run all 2024 scripts]

#!/usr/bin/env python3
import os, subprocess, glob, time, sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.cm import ScalarMappable

def get_file_line_count(file_path):
    """Get the number of lines in a script file."""
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
        return len(lines)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

def run_script(file_path):
    """Run a script based on its file extension and time its execution."""
    _, extension = os.path.splitext(file_path)
    
    try:
        # Ignore .txt files (such as input files) and .png images
        if extension == '.txt' or extension == '.png' or extension == '.exe':
            return None  # Skip these files
        
        # Print the file name (not the full path) before running
        file_name = os.path.basename(file_path)

        if os.path.basename(file_path).startswith("Alt"):
            print(f"Skipping script: {file_name} (starts with 'Alt')")
            return None
        else:
            print(f"\nRunning script: {file_name}")

        # Record start time
        start_time = time.time()

        if extension == '.py':
            # Run Python scripts with SUPPRESS_PLOT environment variable
            subprocess.run(['python', file_path], check=True, env={**os.environ, "SUPPRESS_PLOT": "1"})
        elif extension == '.c':
            # Compile and run C files
            executable = file_path.replace('.c', '')
            subprocess.run(['gcc', file_path, '-o', executable], check=True)
            subprocess.run([executable], check=True)
        elif extension == '.rb':
            # Run Ruby scripts
            subprocess.run(['ruby', file_path], check=True)
        elif extension == '.jl':
            # Run Julia scripts
            subprocess.run(['julia', file_path], check=True)
        else:
            print(f"Unsupported file type for {file_path}. Skipping.")

        # Calculate elapsed time for this script
        elapsed_time = time.time() - start_time
        print(f"Finished running {file_name} in {elapsed_time:.2f} seconds.")
        
        # Get the file extension and line count
        extension = os.path.splitext(file_path)[1]
        line_count = get_file_line_count(file_path)
        
        return extension, line_count, elapsed_time
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute {file_path}: {e}")
        return None

def generate_gradient_around_color(center_color, num_steps=10):
    # Convert the center color from hex to RGB
    center_rgb = mcolors.hex2color(center_color)
    
    # Create lighter and darker versions of the color by modifying the brightness
    lighter_colors = [tuple(min(1, c + i * 0.05) for c in center_rgb) for i in range(num_steps)]
    darker_colors = [tuple(max(0, c - i * 0.05) for c in center_rgb) for i in range(num_steps)]
    
    # Combine them to form a full gradient (darker -> center -> lighter)
    full_gradient = darker_colors[::-1] + [center_rgb] + lighter_colors
    return full_gradient[::-1]

def create_table(file_info, times_taken, Year, repo_dir):
    total_elapsed_time = sum(times_taken.values())
    percentages = [(time / total_elapsed_time) * 100 for time in times_taken.values()]
    days = list(times_taken.keys())
    table_path = os.path.join(repo_dir, f"{Year}_RunTime_table.txt")

    with open(table_path, 'w') as f:
        f.write(f"{'Day':<6}{'Time (s)':<12}{'Percentage':<15}{'Extension':<12}{'Line Count':<12}\n")
        f.write("-" * 60 + "\n")
        for i, day in enumerate(days):
            file_path = list(file_info.keys())[i]
            extension, line_count, _ = file_info[file_path]
            f.write(f"{day:<6}{times_taken[day]:<12.2f}{percentages[i]:<15.2f}{extension:<12}{line_count:<12}\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total Time: {total_elapsed_time:.2f} seconds\n")
        f.write(f"Average Time: {np.mean(list(times_taken.values())):.2f} seconds\n")
        f.write(f"Median Time: {np.median(list(times_taken.values())):.2f} seconds\n")

    print(f"Table saved to {table_path}")

def create_plot(days, times, percentages, file_info, total_elapsed_time, average_time, median_time,
                max_time, min_time, max_day, min_day, challenge, Year, center_color="#4CAF50"):
    color_gradient = generate_gradient_around_color(center_color)
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_gradient", color_gradient)

    norm = mcolors.Normalize(vmin=min(percentages), vmax=max(percentages))
    bar_colors = [cmap(norm(p)) for p in percentages]

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.bar(days, times, color=bar_colors, zorder=3)
    max_y_value = max(times)
    ax.set_ylim(0, max_y_value * 1.25)

    for i, (bar, percentage) in enumerate(zip(bars, percentages)):
        height = bar.get_height()
        label_position = height + 0.15
        file_path = list(file_info.keys())[i]
        extension, line_count, _ = file_info[file_path]
        ax.text(bar.get_x() + bar.get_width() / 2, label_position,
                f"({extension}) {line_count} lines", ha='center', va='bottom', fontsize=10, color='black', rotation=90)

    ax.plot(max_day, max_time, 'rx', label=f"Max ({max_time:.2f}s)", markersize=5, zorder=5)
    ax.plot(min_day, min_time, 'bx', label=f"Min ({min_time:.2f}s)", markersize=5, zorder=5)

    ax.axhline(0, color='#000000', linestyle='-', zorder=5)
    ax.axhline(average_time, color='#008000', linestyle=':', label=f'Average: {average_time:.2f}s')
    ax.axhline(median_time, color='#800080', linestyle=':', label=f'Median: {median_time:.2f}s')

    ax.set_xticks(days)
    ax.set_xticklabels([f'Day {day}' for day in days], rotation=45, ha='right')
    ax.set_ylabel("Time Taken (seconds)", fontsize=14)
    ax.set_title(f'{challenge} Year {Year}: Total Time is {total_elapsed_time:.2f} seconds',
                    fontsize=18, fontweight='bold')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, zorder=2)
    ax.legend(loc='upper left', bbox_to_anchor=(0, 1), fontsize=11, frameon=True, facecolor='white', edgecolor='black')
    plt.tight_layout()

    cbar = plt.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax)
    cbar.set_label('Relative Percentage of Total Time (%)', fontsize=12)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    plot_path = os.path.join(script_dir, f"{Year}_RunTime_plot.png")
    plt.savefig(plot_path, bbox_inches='tight')
    plt.show()
    print(f"Plot saved to {plot_path}")

def main(challenge, Year, days_to_run, center_color="#4CAF50"):
    total_start_time = time.time()
    print(f"Running scripts for days: {days_to_run}")

    # Define the base directory to the Year folder specifically
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{Year}")
    base_dir = os.path.abspath(os.path.join(os.getcwd(), f"{Year}"))
    selected_dir = repo_dir

    if not os.path.isdir(selected_dir):
        print(f"Directory '{selected_dir}' does not exist.")
        return

    times_taken = {}
    file_info = {}

    for day_dir in os.listdir(selected_dir):
        day_path = os.path.join(selected_dir, day_dir)
        if os.path.isdir(day_path) and day_dir.isdigit():
            padded_day_dir = day_dir.zfill(2)
            day_number = int(day_dir)
            if day_number in days_to_run:
                day_start_time = time.time()

                for script_file in glob.glob(f"{day_path}/*"):
                    if padded_day_dir in script_file:
                        result = run_script(script_file)
                        if result:
                            extension, line_count, elapsed_time = result
                            file_info[script_file] = (extension, line_count, elapsed_time)

                times_taken[day_number] = time.time() - day_start_time

    total_elapsed_time = sum(times_taken.values())
    print(f"\nTotal time to execute specified scripts: {total_elapsed_time:.2f} seconds.")

    if times_taken:
        days = list(times_taken.keys())
        times = list(times_taken.values())
        percentages = [(time / total_elapsed_time) * 100 for time in times]
        average_time = np.mean(times)
        median_time = np.median(times)
        max_time = max(times)
        min_time = min(times)
        max_day = days[times.index(max_time)]
        min_day = days[times.index(min_time)]

        create_plot(days, times, percentages, file_info, total_elapsed_time, average_time, 
                    median_time, max_time, min_time, max_day, min_day, challenge, Year, center_color)
        create_table(file_info, times_taken, Year, repo_dir=selected_dir)

    print(f"Total script execution time: {time.time() - total_start_time:.2f} seconds.")

# Red shades
red = "#D32F2F"           # Dark Red
bright_red = "#FF2010"    # Bright Red

# Green shades
green = "#388E3C"         # Dark Green
lime_green = "#32CD32"    # Lime Green

# Yellow shades
yellow = "#FFEB3B"        # Yellow
neon_yellow = "#FFFF00"   # Neon Yellow

# Blue shades
dark_blue = "#303F9F"     # Dark Blue
light_blue = "#03A9F4"    # Light Blue
blue = "#0000ff"

# Neutral colors
black = "#212121"         # Black

orange = "#FFA500"

if __name__ == "__main__":
    Year = 2024
    challenge = 'Challenge'
    problems = range(1, 26)
    main(challenge, Year, problems, orange)