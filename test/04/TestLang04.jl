#= Challenge Code - HelloWorld, Day 4
Solution Started: August 18, 2025
Puzzle Link: https://challengecode.com/HelloWorld/day/4
Solution by: Your Name
Brief: [Code/Problem Description]
=#

#!/usr/bin/env julia

using Printf, DelimitedFiles
# Load the input data from the specified file path
const INPUT_FILE = "Lang04_input.txt"
const INPUT_FILE_PATH = joinpath(dirname(@__FILE__), INPUT_FILE)

function main()
    # Read the input data
    input_data = readlines(INPUT_FILE_PATH)
    println("Input Data: ", input_data)
    println("Hello, World!\n-From Julia")
end

main()
