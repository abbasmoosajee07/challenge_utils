
#!/usr/bin/env python3
import os
import subprocess
import time
import psutil

def get_file_line_count(file_path):
    """Get the number of lines in a script file."""
    try:
        with open(file_path, "r") as file:
            return len(file.readlines())
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

def get_file_size(file_path):
    """Get the size of a file in kilobytes."""
    try:
        return os.path.getsize(file_path) / 1024
    except Exception as e:
        print(f"Error getting size of {file_path}: {e}")
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

        line_count = get_file_line_count(file_path)
        file_size = get_file_size(file_path)

        elapsed_time = time.time() - start_time
        print(f"Finished running {file_name} in {elapsed_time:.2f} seconds with peak memory usage {peak_memory:.2f} MB. ")

        return extension, line_count, file_size, elapsed_time, peak_memory
    except subprocess.CalledProcessError as e:
        print(f"Error executing {file_name}: {e}")
        return None