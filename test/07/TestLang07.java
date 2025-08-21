/* Challenge Code - HelloWorld, Day 7
Solution Started: August 21, 2025
Puzzle Link: https://challengecode.com/HelloWorld/day/7
Solution by: Your Name
Brief: [Code/Problem Description] */

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class TestLang07 {
    public static void main(String[] args) {
        // Use the first argument if provided, otherwise default
        String fileName = (args.length >= 1) ? args[0] : "Lang07_input.txt";
        File file = new File(fileName);
        System.out.println("Input Data:");

        try (Scanner sc = new Scanner(file)) {
            while (sc.hasNextLine()) {
                System.out.println(sc.nextLine());
            }
        } catch (FileNotFoundException e) {
            System.err.println("File not found: " + fileName);
            e.printStackTrace();
        }

        System.out.println("Hello, World!\\n- From Java");
    }
}
