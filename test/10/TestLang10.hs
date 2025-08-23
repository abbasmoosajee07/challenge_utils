{-
Challenge Code - HelloWorld, Day 10
Solution Started: August 23, 2025
Puzzle Link: https://challengecode.com/HelloWorld/day/10
Solution by: Your Name
Brief: [Code/Problem Description]
-}

import System.Environment (getArgs)
import System.Exit (exitFailure)
import System.IO (withFile, IOMode(ReadMode), hGetContents, hPutStrLn, stderr)

-- Define the input file name
inputFile :: String
inputFile = "Lang10_input.txt"

-- Function to read input file
readInput :: String -> IO ()
readInput filename = do
    content <- safeReadFile filename
    putStrLn "Input data:"
    putStr content

-- Safe file reading with error handling
safeReadFile :: String -> IO String
safeReadFile filename = do
    result <- safeOpen filename
    case result of
        Just content -> return content
        Nothing -> do
            hPutStrLn stderr "Unable to open file"
            exitFailure

-- Helper to attempt opening a file
safeOpen :: String -> IO (Maybe String)
safeOpen filename = do
    -- Use try to catch exceptions (requires import Control.Exception if needed)
    content <- readFile filename
    return (Just content)

-- Main function
main :: IO ()
main = do
    args <- getArgs
    let input_file = if not (null args) then head args else inputFile
    readInput input_file
    putStrLn "\nHello, World!\n-From Haskell"
