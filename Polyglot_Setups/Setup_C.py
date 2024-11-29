## Setup for C Script
import os

def create_c_script(
        day=1, year=2024, author='your name',
        header_text="Test", repo_dir=""):
    """
    Sets up the folder structure, C script, and input file for a Coding challenge.

    Parameters:
        day (int): The day/problem of the challenge (1-25).
        year (int): The year/level of the challenge.
        author (str): Name of the script author.
        header_text (str): Header text for the C script.
        repo_dir (str): Base directory for the Challenge Code repository.

    Returns:
        None
    """
    # Zero-pad the day to ensure two-digit formatting (e.g., "01", "12")
    formatted_day = str(day).zfill(2)
    
    # Define the directory structure for the specified year and day
    challenge_dir = os.path.join(repo_dir, str(year), formatted_day)
    
    # Define the filename for the C script and its full path
    script_filename = f'{year}Day{formatted_day}.c'
    script_filepath = os.path.join(challenge_dir, script_filename)
    
    # Ensure the base directory for the challenge exists
    os.makedirs(challenge_dir, exist_ok=True)

    # Create the C script if it doesn't already exist
    if not os.path.exists(script_filepath):
        # Template content for the C script
        script_content = f'''/*
{header_text}*/

#include <stdio.h>
#include <stdlib.h>

// Define the input file name
#define INPUT_FILE "Day{formatted_day}_input.txt"

// Function to read input file
void read_input(const char *filename) {{
    FILE *file = fopen(filename, "r");
    if (!file) {{
        perror("Unable to open file");
        exit(EXIT_FAILURE);
    }}
    
    char line[256];
    printf("Input data:\\n");
    while (fgets(line, sizeof(line), file)) {{
        printf("%s", line);
    }}
    
    fclose(file);
}}

// Main function
int main() {{
    printf("Challenge Code - Day {day}, Year {year}\\n");
    
    // Read input data
    read_input(INPUT_FILE);
    
    // Your solution logic goes here
    
    return 0;
}}
'''
        # Write the template content to the C script file
        with open(script_filepath, 'w') as script_file:
            script_file.write(script_content)

        print(f"Created C script '{script_filename}'.")
    else:
        print(f"C script '{script_filename}' already exists.")

    # Display the full path to the C script
    print(f"Full Path: {script_filepath}")
