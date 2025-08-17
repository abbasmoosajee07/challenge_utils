import sys
from pathlib import Path

# Get the absolute path to the parent directory containing challenge_utils
challenge_utils_path = str(Path(__file__).parent.parent)  # Goes up one level
# Add to Python path (only if not already there)
if challenge_utils_path not in sys.path:
    sys.path.insert(0, challenge_utils_path)

# Now import your module
from ChallengeBenchmarks import ChallengeBenchmarks
# Example usage
if __name__ == "__main__":

    base_dir = Path.cwd() / str("test_challenge")
    script_dir = Path(__file__).parent.resolve()
    selected_dir = base_dir
    config_file = "test_challenge.json"
    PROBLEMS_TO_RUN = list(range(1, 26))  # Problems 1-25

    analyzer = ChallengeBenchmarks(
        base_dir = selected_dir,
        config_file = config_file,
    )

    results = analyzer.analyze(
        problems_to_run= PROBLEMS_TO_RUN,  # Problems 1-25
        iterations=3,
        save_results=True,
    )

    print("\nAnalysis complete!")
    print(results.head(25))