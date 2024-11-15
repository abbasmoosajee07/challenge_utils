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
        with open(file_path, 'r') as file:
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

def parse_days_input(days_input):
    """Parse the input string for days (e.g., '1,2,3' or '1-5')."""
    days_to_run = []

    # Split by commas for cases like "1,2,3"
    for part in days_input.split(','):
        # Handle range (e.g., "1-5")
        if '-' in part:
            try:
                start, end = part.split('-')
                days_to_run.extend(range(int(start), int(end) + 1))
            except ValueError:
                print(f"Error: Invalid range format '{part}'")
                continue
        else:
            try:
                # Handle single day input (e.g., "5")
                days_to_run.append(int(part))
            except ValueError:
                print(f"Error: Invalid day format '{part}'")
                continue

    return days_to_run

def generate_gradient_around_color(center_color, num_steps=10):
    # Convert the center color from hex to RGB
    center_rgb = mcolors.hex2color(center_color)
    
    # Create lighter and darker versions of the color by modifying the brightness
    lighter_colors = [tuple(min(1, c + i * 0.05) for c in center_rgb) for i in range(num_steps)]
    darker_colors = [tuple(max(0, c - i * 0.05) for c in center_rgb) for i in range(num_steps)]
    
    # Combine them to form a full gradient (darker -> center -> lighter)
    full_gradient = darker_colors[::-1] + [center_rgb] + lighter_colors
    return full_gradient[::-1]

def main(challenge, Year, center_color="#4CAF50"):  # Now you only need to specify the center color
    # Record the start time of the entire process
    total_start_time = time.time()

    # Argument handling for the day range
    if len(sys.argv) < 2:
        print("No specific days provided. Running scripts for all days.")
        days_to_run = range(1, 26)  # Assume there are 25 days (1-25)
    else:
        days_input = sys.argv[1]  # Get the input for days
        days_to_run = parse_days_input(days_input)
    
    print(f"Running scripts for days: {days_to_run}")

    # Define the base directory to the Year folder specifically
    base_dir = os.path.abspath(os.path.join(os.getcwd(), f"{Year}"))
    if not os.path.isdir(base_dir):
        print(f"Directory '{base_dir}' does not exist.")
        return
    
    # Dictionary to track time for each day
    times_taken = {}

    # Dictionary to track the file extensions, line counts, and times
    file_info = {}

    # Traverse only the 'Day' subdirectories within specific Year
    for day_dir in os.listdir(base_dir):
        day_path = os.path.join(base_dir, day_dir)
        
        # Check if the directory name is a digit (Day folder)
        if os.path.isdir(day_path) and day_dir.isdigit():
            padded_day_dir = day_dir.zfill(2)  # Pads day numbers to two digits (e.g., '01', '02')
            
            # Run the script if this day is in the specified range or list
            day_number = int(day_dir)
            if day_number in days_to_run:
                # Track the start time for this day
                day_start_time = time.time()

                # Find all Python, Ruby, and C files in the padded day directory
                for script_file in glob.glob(f"{day_path}/*"):
                    if padded_day_dir in script_file:  # Only run files that match the padded day
                        result = run_script(script_file)
                        if result:
                            extension, line_count, elapsed_time = result
                            file_info[script_file] = (extension, line_count, elapsed_time)

                # Calculate the time taken for this day and store it
                day_elapsed_time = time.time() - day_start_time
                times_taken[day_number] = day_elapsed_time

    # Calculate total elapsed time for the entire process
    total_elapsed_time = sum(times_taken.values())  # Sum the times for each day
    print(f"\nTotal time to execute specified scripts: {total_elapsed_time:.2f} seconds.")

    # Create a graph to visualize the time taken for each day
    if times_taken:
        days = list(times_taken.keys())
        times = list(times_taken.values())

        # Calculate percentage for each day's time
        percentages = [(time / total_elapsed_time) * 100 for time in times]

        # Calculate additional statistics
        average_time = np.mean(times)
        median_time = np.median(times)
        std_dev_time = np.std(times)
        max_time = max(times)
        min_time = min(times)

        # Generate the gradient based on the specified center color
        color_gradient = generate_gradient_around_color(center_color)
        
        # Create a colormap from the generated gradient
        cmap = mcolors.LinearSegmentedColormap.from_list("custom_gradient", color_gradient)
        
        # Normalize and apply color gradient to bars
        norm = mcolors.Normalize(vmin=min(percentages), vmax=max(percentages))
        bar_colors = [cmap(norm(p)) for p in percentages]

        # Plot the time taken for each day with gradient colors
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.bar(days, times, color=bar_colors, zorder=3)

        # After plotting the bars, calculate the current maximum y-value (max_time)
        max_y_value = max(times)  # Or you can use the highest value from your data if needed

        # Set the upper limit of the y-axis to be 25% greater than the current maximum
        ax.set_ylim(0, max_y_value * 1.25)  # Extends the y-axis by 25%

        # Add percentage labels on top of each bar (adjusted to avoid overlap)
        for i, (bar, percentage) in enumerate(zip(bars, percentages)):
            height = bar.get_height()
            # Label position dynamically to avoid overlap with min/max labels
            label_position = height + 0.15 # if height < max_time * 0.75 else height - 0.15
            file_path = list(file_info.keys())[i]
            extension, line_count, _ = file_info[file_path]
            ax.text(bar.get_x() + bar.get_width() / 2, label_position,
                    f"({extension}) {line_count} lines", ha='center', va='bottom', fontsize=10, color='black', rotation=90)

        # Highlight the maximum and minimum time days
        max_day = days[times.index(max_time)]
        min_day = days[times.index(min_time)]
        # Replace the text labels with blank points (markers) for Max and Min
        ax.plot(max_day, max_time, 'rx', label=f"Max ({max_time:.2f}s)", markersize=5, zorder=5)
        ax.plot(min_day, min_time, 'bx', label=f"Min ({min_time:.2f}s)", markersize=5, zorder=5)

        # Plot average, median, and standard deviation lines
        ax.axhline(0, color='#000000', linestyle='-',zorder=5)  # Zero base (#000000)
        ax.axhline(average_time, color='#008000', linestyle=':', label=f'Average: {average_time:.2f}s')  # Green (#008000)
        ax.axhline(median_time, color='#800080', linestyle=':', label=f'Median: {median_time:.2f}s')  # Purple (#800080)
        # ax.axhline(average_time + std_dev_time, color='#FFA500', linestyle=':', label=f'1 Std Dev: {average_time + std_dev_time:.2f}s')  # Orange (#FFA500)
        # ax.axhline(average_time - std_dev_time, color='#FFA500', linestyle=':')  # Orange (#FFA500)

        # Customize plot labels and title
        ax.set_xticks(days)
        ax.set_xticklabels([f'Day {day}' for day in days], rotation=45, ha='right')
        ax.set_ylabel("Time Taken (seconds)", fontsize=14)
        ax.set_title(f'{challenge} Year {Year}: Total Time is {total_elapsed_time:.2f} seconds',fontsize=18, fontweight='bold')

        # Add grid, legend, and colorbar
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, zorder=2)
        ax.legend(loc='upper left', bbox_to_anchor=(0, 1), fontsize=11, frameon=True, facecolor='white', edgecolor='black')
        plt.tight_layout()

        # Add colorbar to explain the color gradient
        cbar = plt.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax)
        cbar.set_label('Relative Percentage of Total Time (%)', fontsize=12)

        # Define the path for saving the plot
        script_dir = os.path.dirname(os.path.abspath(__file__))
        plot_path = os.path.join(script_dir, f"{Year}_RunTime_plot.png")

        # Save the plot to the specified path before displaying
        plt.savefig(plot_path, bbox_inches='tight')

        # Display the plot
        plt.show()

    # Total process elapsed time
    total_process_time = time.time() - total_start_time
    print(f"Total script execution time: {total_process_time:.2f} seconds.")

# Red shades
red = '#D32F2F'           # Dark Red
bright_red = "#FF2010"    # Bright Red

# Green shades
green = '#388E3C'         # Dark Green
lime_green = '#32CD32'    # Lime Green

# Yellow shades
yellow = '#FFEB3B'        # Yellow
neon_yellow = "#FFFF00"   # Neon Yellow

# Blue shades
dark_blue = '#303F9F'     # Dark Blue
light_blue = '#03A9F4'    # Light Blue

# Neutral colors
black = '#212121'         # Black


if __name__ == "__main__":
    Year = 2024
    challenge = 'Challenge'
    main(challenge, Year, lime_green)