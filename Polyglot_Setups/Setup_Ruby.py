## Setup for Ruby Script
#!/usr/bin/env python3
import os

def create_ruby_script(
        day=1, year=2024, author='your name',
        header_text="Test", repo_dir=""):
    """
    Sets up the folder structure, Ruby script, and input file for a Coding challenge.

    Parameters:
        day (int): The day/problem of the challenge (1-25).
        year (int): The year/level of the challenge.
        author (str): Name of the script author.
        header_text (str): Header text for the Ruby script.
        repo_dir (str): Base directory for the Challenge Code repository.

    Returns:
        None
    """
    # Zero-pad the day to ensure two-digit formatting (e.g., "01", "12")
    formatted_day = str(day).zfill(2)
    
    # Define the directory structure for the specified year and day
    challenge_dir = os.path.join(repo_dir, str(year), formatted_day)
    
    # Define the filename for the Ruby script and its full path
    script_filename = f'{year}Day{formatted_day}.rb'
    script_filepath = os.path.join(challenge_dir, script_filename)
    
    # Ensure the base directory for the challenge exists
    os.makedirs(challenge_dir, exist_ok=True)

    # Create the Ruby script if it doesn't already exist
    if not os.path.exists(script_filepath):
        # Template content for the Ruby script
        script_content = f'''=begin
{header_text}=end

#!/usr/bin/env ruby

require 'pathname'

# Define file name and extract complete path to the input file
D{formatted_day}_file = "Day{formatted_day}_input.txt"
D{formatted_day}_file_path = Pathname.new(__FILE__).dirname + D{formatted_day}_file

# Read the input data
input_data = File.readlines(D{formatted_day}_file_path).map(&:strip)

# Main execution
if __FILE__ == $0
  puts "Challenge Code - Day {day}, Year {year}"
  puts {'input_data'}

  # Your solution logic goes here
end
'''
        # Write the template content to the Ruby script file
        with open(script_filepath, 'w') as script_file:
            script_file.write(script_content)

        print(f"Created Ruby script '{script_filename}'.")
    else:
        print(f"Ruby script '{script_filename}' already exists.")

    # Display the full path to the Ruby script
    print(f"Full Path: {script_filepath}")
