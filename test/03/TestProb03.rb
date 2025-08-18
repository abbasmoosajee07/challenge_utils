=begin
Challenge Code - HelloWorld, Day 3
Solution Started: August 18, 2025
Puzzle Link: https://challengecode.com/HelloWorld/day/3
Solution by: Your Name
Brief: [Code/Problem Description]
=end

#!/usr/bin/env ruby

require 'pathname'

# Define file name and extract complete path to the input file
input_file = "Day03_input.txt"
input_file_path = Pathname.new(__FILE__).dirname + input_file

# Read the input data
input_data = File.readlines(input_file_path).map(&:strip)

# Main execution
if __FILE__ == $0
  puts "Input Data: #{input_data}"

  puts "Hello, World!\n-From Ruby"
  # Your solution logic goes here
end

