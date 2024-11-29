## Setup for Text File
#!/usr/bin/env python3
import os

def create_txt_file(
        day=1, year=2024, author='your name',
        header_text="Test", repo_dir=""):
    """
    Sets up the folder structure, Text File, and input file for a Coding challenge.

    Parameters:
        day (int): The day/problem of the challenge (1-25).
        year (int): The year/level of the challenge.
        author (str): Name of the script author.
        header_text (str): Header text for the Text File.
        repo_dir (str): Base directory for the Challenge Code repository.

    Returns:
        None
    """
    # Zero-pad the day to ensure two-digit formatting (e.g., "01", "12")
    formatted_day = str(day).zfill(2)
    
    # Define the directory structure for the specified year and day
    challenge_dir = os.path.join(repo_dir, str(year), formatted_day)
    
    # Define the filename for the Text File and its full path
    txt_filename = f'Day{formatted_day}_input.txt'
    txt_filepath = os.path.join(challenge_dir, txt_filename)
    
    # Ensure the base directory for the challenge exists
    os.makedirs(challenge_dir, exist_ok=True)

    # Create the Text File if it doesn't already exist
    if not os.path.exists(txt_filepath):
        # Template content for the Text File
        file_content = f''''''

        # Write the template content to the Text File
        with open(txt_filepath, 'w') as txt_file:
            txt_file.write(file_content)

        print(f"Created Text File '{txt_filename}'.")
    else:
        print(f"Text File '{txt_filename}' already exists.")

    # Display the full path to the Text File
    print(f"Full Path: {txt_filepath}")
