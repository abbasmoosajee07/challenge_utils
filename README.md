# Challenge Utils

This repo contains a python workspace to benchmark time, memory and other properties for a series of solution scripts generally designed for coding challenges.

to install create a set_up pkg in working directory, for the challenge_utils folder and then
`pip install -e.` in terminal.


#!/bin/bash

# Add challenge_utils as a submodule (root directory)
git submodule add https://github.com/abbasmoosajee07/challenge_utils.git challenge_utils

# Initialize and update the submodule
git submodule update --init --recursive

# Commit the changes
git add .gitmodules challenge_utils
git commit -m "Add challenge_utils submodule"

# Push to main branch
git push origin main

# Verification
echo "Submodule added. Verification:"
git submodule status
cat .gitmodules

