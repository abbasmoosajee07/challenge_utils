import subprocess
import time
import psutil
from pathlib import Path

from typing import Dict, List, Tuple, Optional, Dict, Any
class ScriptRunner:
    """Handles execution of challenge solution scripts and performance measurement"""
    supported_languages =  ["py", "jl", "rb", "js", "c"]

    def __init__(self):
        self.times_taken: Dict[int, List[float]] = {}
        self.file_info: Dict[int, Tuple[str, int, float]] = {}
        self.peak_memory_usage: Dict[int, List[float]] = {}

    def get_file_line_count(self, file_path: Path) -> int:
        try:
            with file_path.open("r", encoding="utf-8") as file:
                return len(file.readlines())
        except Exception:
            return 0

    def get_file_size(self, file_path: Path) -> float:
        try:
            return file_path.stat().st_size / 1024
        except Exception:
            return 0.0

    def monitor_memory_usage(self, process: subprocess.Popen) -> float:
        try:
            peak_memory = 0.0
            while process.poll() is None:
                mem_info = psutil.Process(process.pid).memory_info()
                peak_memory = max(peak_memory, mem_info.rss)
                time.sleep(0.1)
            return peak_memory / (1024 ** 2)  # MB
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0

    def _record_result(self, problem_number: int, result: Tuple[str, int, float, float, float]):
        ext, lines, size, time_ms, memory = result
        if problem_number not in self.times_taken:
            self.times_taken[problem_number] = []
            self.peak_memory_usage[problem_number] = []
            self.file_info[problem_number] = (
                f"{ext}", lines, size
            )
        self.times_taken[problem_number].append(time_ms)
        self.peak_memory_usage[problem_number].append(memory)

    def process_directory(self, base_dir: Path, problems_to_run: List[int],
                        iterations: int, config: object):
        for iteration in range(iterations):
            print(f"\nIteration run: {iteration + 1}/{iterations}\n")
            for problem_no in problems_to_run:
                problem_folder = config.get_problem_folder(problem_no)
                problem_path = base_dir / problem_folder
                for lang in self.supported_languages:
                    solution_pattern = config.get_solution_filename(problem_no, lang)
                    text_input = config.get_property("text_input").format(problem_no=problem_no)
                    input_path = problem_path / f"{text_input}.txt"
                    for solution_file in problem_path.glob(solution_pattern):
                        result = self.run_script(solution_file, input_path)
                        if result:
                            self._record_result(problem_no, result)

    def run_script(self, file_path: Path, text_file = None) -> Optional[Tuple[str, int, float, float, float]]:
        extension = file_path.suffix.lower()
        file_name = file_path.name

        # Early exit conditions
        if extension in {'.txt', '.png', '.exe'} or file_name.startswith("Alt"):
            print(f"Skipping script: {file_name}" + 
                (" (unsupported extension)" if extension in {'.txt', '.png', '.exe'} else " (starts with 'Alt')"))
            return None

        # Command mapping for different file types
        command_map = {
            '.py': ['python', str(file_path)],
            '.c': {
                'compile': ['gcc', str(file_path), '-o', str(file_path.with_suffix(''))],
                'run': [str(file_path.with_suffix('')), text_file]
            },
            '.rb': ['ruby', str(file_path)],
            '.jl': ['julia', str(file_path)],
            '.js': ['node', str(file_path)]
        }

        if extension not in command_map:
            print(f"Unsupported file type for {file_name}. Skipping.")
            return None

        print(f"\nRunning script: {file_name}")
        start_time = time.time()
        process = None

        try:
            if extension in ['.c']:
                subprocess.run(command_map[extension]['compile'], check=True)
                process = subprocess.Popen(command_map[extension]['run'])
            else:
                process = subprocess.Popen(command_map[extension])

            peak_memory = self.monitor_memory_usage(process)
            process.wait()

            return (
                extension,
                self.get_file_line_count(file_path),
                self.get_file_size(file_path),
                (time.time() - start_time) * 1000,  # ms
                peak_memory
            )
        except subprocess.CalledProcessError as e:
            print(f"Error executing {file_name}: {e}")
            return None
        finally:
            if process and process.poll() is None:
                process.terminate()

