from pathlib import Path
from challenge_utils import ChallengeBenchmarks

if __name__ == "__main__":

    base_dir = Path.cwd() / str("test_config")
    script_dir = Path(__file__).parent.resolve()
    selected_dir = script_dir
    config_file = "test_config.json"

    PROBLEMS_TO_RUN = list(range(1, 26))  # Problems 1-25

    analyzer = ChallengeBenchmarks(
        base_dir = selected_dir,
        config_file = config_file,
    )

    results = analyzer.analyze(
        problems_to_run= PROBLEMS_TO_RUN,  # Problems 1-25
        iterations=3,
        save_results=True,
        custom_dir= script_dir / "analysis"
    )

    print("\nAnalysis complete!")
    print(results.head(25))

