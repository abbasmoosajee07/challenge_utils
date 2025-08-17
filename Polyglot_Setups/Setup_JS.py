#!/usr/bin/env python3
import os

def create_javascript_script(
        day=1, year=2024, author='your name',
        header_text="Challenge Header", repo_dir=""):
    """
    Sets up the folder structure, JavaScript script, and input file for a coding challenge.

    Parameters:
        day (int): The day/problem of the challenge (1-25).
        year (int): The year/level of the challenge.
        author (str): Name of the script author.
        header_text (str): Header comment at the top of the script.
        repo_dir (str): Base directory where the challenge folder should be created.

    Returns:
        None
    """
    formatted_day = str(day).zfill(2)
    challenge_dir = os.path.join(repo_dir, str(year), formatted_day)
    script_filename = f'{year}Day{formatted_day}.js'
    script_filepath = os.path.join(challenge_dir, script_filename)
    input_filename = f'Day{formatted_day}_input.txt'
    input_filepath = os.path.join(challenge_dir, input_filename)

    os.makedirs(challenge_dir, exist_ok=True)

    # JS script template content
    script_content = f'''/**
 * {header_text}
 * Day {formatted_day} - Year {year}
 * Author: {author}
 */

import fs from 'fs';
import path from 'path';
import {{ fileURLToPath }} from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

(function main() {{
    const inputPath = path.join(__dirname, '{input_filename}');
    const input = fs.readFileSync(inputPath, 'utf-8').trim().split('\\n');

    console.log("Input:", input);

    // Your solution goes here
}})();

'''

    # Write JS file if it doesn't exist
    if not os.path.exists(script_filepath):
        with open(script_filepath, 'w') as f:
            f.write(script_content)
        print(f"Created JavaScript file '{script_filename}'.")
    else:
        print(f"JavaScript file '{script_filename}' already exists.")

    # Create a blank input file if it doesn't exist
    if not os.path.exists(input_filepath):
        with open(input_filepath, 'w') as f:
            f.write('')
        print(f"Created input file '{input_filename}'.")
    else:
        print(f"Input file '{input_filename}' already exists.")

    print(f"Full Path: {script_filepath}")
