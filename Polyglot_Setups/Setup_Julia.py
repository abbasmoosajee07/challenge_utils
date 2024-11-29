## Setup for Julia Script
#!/usr/bin/env python3
import os

def create_julia_script(
        day=1, year=2024, author='your name',
        header_text="Test", repo_dir=""):
    """
    Sets up the folder structure, Julia script, and input file for a Coding challenge.

    Parameters:
        day (int): The day/problem of the challenge (1-25).
        year (int): The year/level of the challenge.
        author (str): Name of the script author.
        header_text (str): Header text for the Julia script.
        repo_dir (str): Base directory for the Challenge Code repository.

    Returns:
        None
    """
    # Zero-pad the day to ensure two-digit formatting (e.g., "01", "12")
    formatted_day = str(day).zfill(2)
    
    # Define the directory structure for the specified year and day
    challenge_dir = os.path.join(repo_dir, str(year), formatted_day)
    
    # Define the filename for the Julia script and its full path
    script_filename = f'{year}Day{formatted_day}.jl'
    script_filepath = os.path.join(challenge_dir, script_filename)
    
    # Ensure the base directory for the challenge exists
    os.makedirs(challenge_dir, exist_ok=True)

    # Create the Julia script if it doesn't already exist
    if not os.path.exists(script_filepath):
        # Template content for the Julia script
        script_content = f'''#=
{header_text}=#

#!/usr/bin/env julia

using Printf, DelimitedFiles

# Load the input data from the specified file path
const D{formatted_day}_FILE = "Day{formatted_day}_input.txt"
const D{formatted_day}_FILE_PATH = joinpath(dirname(@__FILE__), D{formatted_day}_FILE)

# Read the input data
input_data = readlines(D{formatted_day}_FILE_PATH)
println(input_data)

'''
        # Write the template content to the Julia script file
        with open(script_filepath, 'w') as script_file:
            script_file.write(script_content)

        print(f"Created Julia script '{script_filename}'.")
    else:
        print(f"Julia script '{script_filename}' already exists.")

    # Display the full path to the Julia script
    print(f"Full Path: {script_filepath}")
