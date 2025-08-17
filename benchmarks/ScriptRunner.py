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

    def run_script(self, file_path: Path) -> Optional[Tuple[str, int, float, float, float]]:
        extension = file_path.suffix
        file_name = file_path.name

        try:
            if extension in ['.txt', '.png', '.exe']:
                return None
            if file_name.startswith("Alt"):
                print(f"Skipping script: {file_name} (starts with 'Alt')")
                return None
            else:
                print(f"Running script: {file_name}")

            start_time = time.time()
            process = None

            if extension == '.py':
                process = subprocess.Popen(['python', str(file_path)])
            elif extension == '.c':
                executable = file_path.with_suffix('')
                subprocess.run(['gcc', str(file_path), '-o', str(executable)], check=True)
                process = subprocess.Popen([str(executable)])
            elif extension == '.rb':
                process = subprocess.Popen(['ruby', str(file_path)])
            elif extension == '.jl':
                process = subprocess.Popen(['julia', str(file_path)])
            elif extension == '.js':
                process = subprocess.Popen(['node', str(file_path)])
            else:
                print(f"Unsupported file type for {file_name}. Skipping.")
                return None

            peak_memory = self.monitor_memory_usage(process)
            process.wait()
            line_count = self.get_file_line_count(file_path)
            file_size = self.get_file_size(file_path)
            elapsed_time = (time.time() - start_time) * 1000  # ms

            return extension, line_count, file_size, elapsed_time, peak_memory
        except subprocess.CalledProcessError as e:
            print(f"Error executing {file_name}: {e}")
            return None

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
            print(f"\nIteration {iteration + 1}/{iterations}")
            for problem_no in problems_to_run:
                problem_folder = config.get_problem_folder(problem_no)
                problem_path = base_dir / problem_folder
                for lang in self.supported_languages:
                    solution_pattern = config.get_solution_filename(problem_no, lang)
                    for solution_file in problem_path.glob(solution_pattern):
                        result = self.run_script(solution_file)
                        if result:
                            self._record_result(problem_no, result)

