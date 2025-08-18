import sys, os, time
from pathlib import Path
from typing import Optional, Dict, Any
from config.ChallengeConfig import ChallengeConfig
from challenge_utils.ScriptBuilder import ScriptBuilder

def main():
    author = "Your Name"
    repo_dir = Path(__file__).parent       # root of your challenge repo
    challenge_dir = repo_dir / "test"
    config_file = "test_config.json"         # your config file name

    builder = ScriptBuilder(author, challenge_dir, config_file)

    # Example: create a Python script for problem 7
    filepath = builder.create_files(
        prob_no=2,
        language="c",
        txt_files=1,
        )
    # print(f"Script created at: {filepath}")

if __name__ == "__main__":
    main()

