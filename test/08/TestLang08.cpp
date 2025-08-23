/* Challenge Code - HelloWorld, Day 8
Solution Started: August 23, 2025
Puzzle Link: https://challengecode.com/HelloWorld/day/8
Solution by: Your Name
Brief: [Code/Problem Description]
*/
#include <iostream>
#include <fstream>
#include <string>
#include <cstdlib>

// Define the input file name
#define INPUT_FILE "Lang08_input.txt"

// Function to read input file
void read_input(const std::string &filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::perror("Unable to open file");
        std::exit(EXIT_FAILURE);
    }

    std::cout << "Input data:" << std::endl;
    std::string line;
    while (std::getline(file, line)) {
        std::cout << line << std::endl;
    }

    file.close();
}

// Main function
int main(int argc, char *argv[]) {
    std::string input_file = (argc > 1) ? argv[1] : INPUT_FILE;
    read_input(input_file);
    std::cout << "\nHello, World!\n-From C++\n";
    return 0;
}
