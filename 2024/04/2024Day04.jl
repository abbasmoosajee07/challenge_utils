#=
Challenge Code - Day 4, Year 2024
Solution Started: Nov 29, 2024
Puzzle Link: https://challengecode.com/2024/day/4
Solution by: your_name
Brief: [Code/Problem Description]
=#

#!/usr/bin/env julia

using Printf, DelimitedFiles

# Load the input data from the specified file path
const D04_FILE = "Day04_input.txt"
const D04_FILE_PATH = joinpath(dirname(@__FILE__), D04_FILE)

# Read the input data
input_data = readlines(D04_FILE_PATH)
println(input_data)

# Example function to test Julia environment
function test_julia_function()
    result = "Julia test function executed!"
    println(result)
    return result
end

# Run the test function to ensure it's working
test_julia_function()
