/*
Challenge Code - Day 2, Year 2024
Solution Started: Nov 29, 2024
Puzzle Link: https://challengecode.com/2024/day/2
Solution by: your_name
Brief: [Code/Problem Description]
*/

#include <stdio.h>

// Function to add two integers
int add(int a, int b) {
    return a + b;
}

// Main function - execution starts here
int main() {
    // Declare two numbers
    int num1 = 5, num2 = 10;
    int sum;

    // Print Hello World message
    printf("Hello, C!\n");

    // Call add function to calculate the sum
    sum = add(num1, num2);

    // Print the result of the addition
    printf("The sum of %d and %d is: %d\n", num1, num2, sum);

    // Return 0 to indicate successful execution
    return 0;
}
