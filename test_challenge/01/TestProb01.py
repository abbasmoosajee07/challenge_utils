# Challenge - Day 1, Year 2024
# Solved in 2024
# Puzzle Link: https://challenge.com/2024/day/1  # Web link without padding
# Solution by: [your_name]
# Brief: [Code/Problem Description]

#!/usr/bin/env python3

import os, re, copy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load the input data from the specified file path
D01_file = "Day01_input.txt"
D01_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), D01_file)

# Read and sort input data into a grid
with open(D01_file_path) as file:
    input_data = file.read().strip().split('\n')

def main():
    """
    Main function to demonstrate reading from a text file.
    """
    try:
        print(f"Reading from file: {D01_file_path}")
        print("File content:")
        for line in input_data:
            print(line)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()