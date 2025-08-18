"""{header_text}"""

#!/usr/bin/env python3
from pathlib import Path

# Load input file
input_file = "{text_placeholder}"
input_path = Path(__file__).parent / input_file

with input_path.open("r", encoding="utf-8") as f:
    data = f.read().splitlines()

print("Input Data:", data)

print("Hello, World\n-From Python")