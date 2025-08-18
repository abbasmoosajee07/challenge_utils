/* {header_text}
*/
#include <stdio.h>
#include <stdlib.h>

// Define the input file name
#define INPUT_FILE "{text_placeholder}"

// Function to read input file
void read_input(const char *filename) {{
    FILE *file = fopen(filename, "r");
    if (!file) {{
        perror("Unable to open file");
        exit(EXIT_FAILURE);
    }}
    
    printf("Input data:");
    char line[256];
    while (fgets(line, sizeof(line), file)) {{
        printf("%s", line);
    }}
    
    fclose(file);
}}

// Main function
int main(int argc, char *argv[]) {{
    const char *input_file = (argc > 1) ? argv[1] : INPUT_FILE;
    read_input(input_file);
    printf("\nHello, World!\n-From C\n");
    return 0;
}}
