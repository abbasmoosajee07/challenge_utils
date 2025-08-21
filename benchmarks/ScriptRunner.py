import subprocess, time, psutil, platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Dict, Any
from ..core.SupportedLangs import Language_Support
class ScriptRunner:
    """Handles execution of challenge solution scripts and performance measurement"""
    supported_languages = Language_Support.supported_languages

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

    def run_script(
        self,
        file_path: Path,
        input_file: Optional[Path] = None,
        cleanup: bool = True
    ) -> Optional[Tuple[str, int, float, float, float]]:
        extension = file_path.suffix.lower()
        file_name = file_path.name

        # Early skip conditions
        if extension in {'.txt', '.png', '.exe'} or file_name.startswith("Alt"):
            reason = " (unsupported extension)" if extension in {'.txt', '.png', '.exe'} else " (starts with 'Alt')"
            print(f"Skipping script: {file_name}{reason}")
            return None

        # Platform-specific executable
        exe_suffix = ".exe" if platform.system() == "Windows" else ""
        exe_path = file_path.with_suffix(exe_suffix)
        input_method = "arg" if input_file else "none"

        # Language config
        language_config = Language_Support(file_path, exe_path, input_method).language_config
        if extension not in language_config:
            print(f"Unsupported file type for {file_name}. Skipping.")
            return None

        config = language_config[extension]
        cleanup_files: list[str] = []

        print(f"Running script: {file_name}")
        start_time = time.time()
        process: Optional[subprocess.Popen] = None

        try:
            # --- Compilation (if needed) ---
            if "compile" in config:
                try:
                    subprocess.run(
                        config["compile"],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    if cleanup and "cleanup" in config:
                        cleanup_files.extend(config["cleanup"])
                except subprocess.CalledProcessError as e:
                    print(f"Compilation failed for {file_name}:\n{e.stderr}")
                    return None

            # --- Prepare execution ---
            run_cmd = config["run"].copy()
            if input_file and config.get("input_method") == "arg":
                run_cmd.append(str(input_file))

            stdin_source = None
            if input_file and config.get("input_method") != "arg":
                stdin_source = open(input_file, "r")

            try:
                process = subprocess.Popen(
                    run_cmd,
                    stdin=stdin_source,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            finally:
                if stdin_source:
                    stdin_source.close()

            # --- Monitor & collect output ---
            peak_memory = self.monitor_memory_usage(process)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                print(f"Execution failed for {file_name} (exit code {process.returncode}):")
                if stderr:
                    print(stderr)
                return None

            if stdout:
                print(stdout)

            return (
                extension,
                self.get_file_line_count(file_path),
                self.get_file_size(file_path),
                (time.time() - start_time) * 1000,  # ms
                peak_memory,
            )

        except FileNotFoundError as e:
            print(f"Required interpreter/compiler not found for {file_name}: {e}\n")
            return None
        except Exception as e:
            print(f"Unexpected error executing {file_name}: {e}\n")
            return None
        finally:
            # Ensure process cleanup
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

            # Remove intermediate files
            for f in cleanup_files:
                try:
                    Path(f).unlink(missing_ok=True)
                except OSError as e:
                    print(f"Warning: Could not remove {f}: {e}\n")
