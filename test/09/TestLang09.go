/* Challenge Code - HelloWorld, Day 9
Solution Started: August 23, 2025
Puzzle Link: https://challengecode.com/HelloWorld/day/9
Solution by: Your Name
Brief: [Code/Problem Description]
*/
package main

import (
	"bufio"
	"fmt"
	"os"
)

// Define the input file name
const INPUT_FILE = "Lang09_input.txt"

// Function to read input file
func read_input(filename string) {
	file, err := os.Open(filename)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Unable to open file: %v\n", err)
		os.Exit(1)
	}
	defer file.Close()

	fmt.Println("Input data:")
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		fmt.Println(scanner.Text())
	}

	if err := scanner.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "Error reading file: %v\n", err)
		os.Exit(1)
	}
}

// Main function
func main() {
	input_file := INPUT_FILE
	if len(os.Args) > 1 {
		input_file = os.Args[1]
	}

	read_input(input_file)
	fmt.Println("\nHello, World!\n-From Go")
}
