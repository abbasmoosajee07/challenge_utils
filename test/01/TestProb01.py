"""Challenge Code - HelloWorld, Day 1
Solution Started: August 18, 2025
Puzzle Link: https://challengecode.com/HelloWorld/day/1
Solution by: Your Name
Brief: [Code/Problem Description]"""

#!/usr/bin/env python3
from pathlib import Path

# Load input file
input_file = "Day01_input.txt"
input_path = Path(__file__).parent / input_file

with input_path.open("r", encoding="utf-8") as f:
    data = f.read().splitlines()

print("Input Data:", data)

print("Hello, World\n-From Python")