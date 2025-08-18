/* Challenge Code - HelloWorld, Day 5
Solution Started: August 18, 2025
Puzzle Link: https://challengecode.com/HelloWorld/day/5
Solution by: Your Name
Brief: [Code/Problem Description]
*/

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function main() {
    const inputPath = path.join(__dirname, 'Day05_input.txt');
    const input = fs.readFileSync(inputPath, 'utf-8').trim().split('\\n');

    console.log("Input Data:", input);
    console.log("Hello, World!\n-From JS");

    // Your solution goes here
};

main();
