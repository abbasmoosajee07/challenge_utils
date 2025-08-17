import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Dict, Any
# Get the absolute path to the parent directory containing challenge_utils
current_dir = str(Path(__file__).parent)
# Add to Python path (only if not already there)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from ChallengeConfig import ChallengeConfig
from benchmarks.ResultsProcessor import ResultsProcessor
from benchmarks.ScriptRunner import ScriptRunner

class ChallengeBenchmarks:
    """Main class that coordinates the performance analysis workflow"""
    def __init__(self, base_dir: Path, config_file: str = ""):
        self.base_dir = base_dir
        self.config = ChallengeConfig(base_dir, config_file)
        self.plot_color = self.config.get_property("plot_color")
        self.challenge_id = self.config.get_property("challenge_id")
        self.challenge_header = self.config.get_property("challenge_header")
        self.script_runner = ScriptRunner()
        self.visualizer = ResultsProcessor(self.challenge_id, self.config.get_property("problem_title"))

    def analyze(self, problems_to_run: List[int], iterations: int = 5, save_results: bool = True,
                custom_dir: Optional[Path] = None):
        print(f"\n{self.challenge_header}")
        print(f"Analyzing problems {min(problems_to_run)} to {max(problems_to_run)} over {iterations} iterations")

        self.script_runner.process_directory(self.base_dir, problems_to_run, iterations, self.config)

        df = self.visualizer.generate_table(
            self.script_runner.file_info,
            self.script_runner.times_taken,
            self.script_runner.peak_memory_usage,
            iterations,
            self.challenge_header,
        )

        if save_results:
            search_dir = custom_dir if custom_dir else self.base_dir
            save_dir = search_dir / "analysis"
            save_dir.mkdir(exist_ok=True)
            output_file = save_dir / f"{self.challenge_id}_Run_Summary.txt"
            self.visualizer.save_table_to_file(output_file)
            self.visualizer.generate_plot(df, self.challenge_header, iterations,
                                            save_dir, self.plot_color, 'linear')
            self.visualizer.generate_plot(df, self.challenge_header, iterations,
                                            save_dir, self.plot_color, 'log')
        return df

