# Challenge - Day 2, Year 2024
# Solved in 2024
# Puzzle Link: https://challenge.com/2024/day/2  # Web link without padding
# Solution by: [your_name]
# Brief: [Code/Problem Description]

#!/usr/bin/env python3

import os, re, copy, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def perform_math_operations(a, b):
    """
    Perform basic mathematical operations on two numbers.
    :param a: First number
    :param b: Second number
    :return: A dictionary with results of operations
    """
    results = {
        "addition": a + b,
        "subtraction": a - b,
        "multiplication": a * b,
        "division": a / b if b != 0 else "Undefined (division by zero)",
        "square_root_a": math.sqrt(a) if a >= 0 else "Undefined (sqrt of negative)",
        "square_root_b": math.sqrt(b) if b >= 0 else "Undefined (sqrt of negative)",
    }
    return results

def read_numbers_from_file(file_path):
    """
    Reads a file containing pairs of numbers, one pair per line.
    :param file_path: Path to the text file containing the numbers.
    :return: A list of tuples, where each tuple contains two numbers.
    """
    pairs = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Strip any leading/trailing whitespace and split by whitespace
                parts = line.strip().split()
                if len(parts) == 2:
                    try:
                        # Convert the parts to floats and store as a tuple
                        a = float(parts[0])
                        b = float(parts[1])
                        pairs.append((a, b))
                    except ValueError:
                        print(f"Skipping invalid line: {line.strip()}")
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    return pairs

def run_tests(file_path):
    """
    Run test cases for the math operations using numbers read from a file.
    :param file_path: Path to the input file containing test data.
    """
    print(f"Reading test data from: {file_path}")
    test_cases = read_numbers_from_file(file_path)
    if not test_cases:
        print("No valid test cases found in the file.")
        return
    
    for i, (a, b) in enumerate(test_cases, start=1):
        print(f"\nTest Case {i}: a = {a}, b = {b}")
        results = perform_math_operations(a, b)
        for operation, result in results.items():
            print(f"  {operation.capitalize()}: {result}")

if __name__ == "__main__":

    # Load the input data from the specified file path
    D02_file = "Day02_input.txt"
    D02_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), D02_file)

    run_tests(D02_file_path)

