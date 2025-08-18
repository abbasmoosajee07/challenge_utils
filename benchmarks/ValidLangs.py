import time, subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Dict, Any

def run_script(self, file_path: Path, input_file: Optional[Path] = None) -> Optional[Tuple[str, int, float, float, float]]:
    extension = file_path.suffix.lower()
    file_name = file_path.name

    # Early exit conditions
    if extension in {'.txt', '.png', '.exe'} or file_name.startswith("Alt"):
        skip_reason = (" (unsupported extension)" if extension in {'.txt', '.png', '.exe'} 
                    else " (starts with 'Alt')")
        print(f"Skipping script: {file_name}{skip_reason}")
        return None

    # Language configuration with compile/run commands
    language_config = {
        # Interpreted languages (direct execution)
        '.py': {
            'run': ['python', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.rb': {
            'run': ['ruby', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.jl': {
            'run': ['julia', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.js': {
            'run': ['node', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.ts': {
            'run': ['ts-node', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.pl': {
            'run': ['perl', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.php': {
            'run': ['php', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.lua': {
            'run': ['lua', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.r': {
            'run': ['Rscript', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.sh': {
            'run': ['bash', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.ps1': {
            'run': ['pwsh', '-File', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.go': {
            'run': ['go', 'run', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        
        # Compiled languages (require compilation step)
        '.c': {
            'compile': ['gcc', str(file_path), '-o', str(file_path.with_suffix(''))],
            'run': [str(file_path.with_suffix(''))],
            'input_method': 'arg',
            'cleanup': [str(file_path.with_suffix(''))]
        },
        '.cpp': {
            'compile': ['g++', str(file_path), '-o', str(file_path.with_suffix(''))],
            'run': [str(file_path.with_suffix(''))],
            'input_method': 'arg',
            'cleanup': [str(file_path.with_suffix(''))]
        },
        '.java': {
            'compile': ['javac', str(file_path)],
            'run': ['java', '-cp', str(file_path.parent), file_path.stem],
            'input_method': 'arg',
            'cleanup': [str(file_path.with_suffix('.class'))]
        },
        '.rs': {
            'compile': ['rustc', str(file_path), '-o', str(file_path.with_suffix(''))],
            'run': [str(file_path.with_suffix(''))],
            'input_method': 'arg',
            'cleanup': [str(file_path.with_suffix(''))]
        },
        
        # Other languages
        '.scala': {
            'run': ['scala', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.swift': {
            'run': ['swift', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.kt': {
            'run': ['kotlin', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.hs': {
            'run': ['runhaskell', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.ml': {
            'run': ['ocaml', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
        '.clj': {
            'run': ['clojure', str(file_path)],
            'input_method': 'arg' if input_file else 'none'
        },
    }

    if extension not in language_config:
        print(f"Unsupported file type for {file_name}. Skipping.")
        return None

    config = language_config[extension]
    print(f"Running script: {file_name}")
    start_time = time.time()
    process = None
    cleanup_files = []

    try:
        # Compilation step for compiled languages
        if 'compile' in config:
            try:
                subprocess.run(
                    config['compile'],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if 'cleanup' in config:
                    cleanup_files.extend(config['cleanup'])
            except subprocess.CalledProcessError as e:
                print(f"Compilation failed for {file_name}:\n{e.stderr}")
                return None

        # Prepare run command based on input method
        run_cmd = config['run'].copy()
        if input_file and config.get('input_method') == 'arg':
            run_cmd.append(str(input_file))

        # Execution step
        stdin_source = None
        if input_file and config.get('input_method') != 'arg':
            stdin_source = open(input_file, 'r')

        process = subprocess.Popen(
            run_cmd,
            stdin=stdin_source,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Monitor memory usage while process runs
        peak_memory = self.monitor_memory_usage(process)
        
        # Wait for process to complete and capture output
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Execution failed for {file_name} (exit code {process.returncode}):")
            if stderr:
                print(stderr)
            return None
        
        # Print program output if successful
        if stdout:
            print(stdout)
        
        return (
            extension,
            self.get_file_line_count(file_path),
            self.get_file_size(file_path),
            (time.time() - start_time) * 1000,  # ms
            peak_memory
        )
        
    except FileNotFoundError as e:
        print(f"Required interpreter/compiler not found for {file_name}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error executing {file_name}: {str(e)}")
        return None
    finally:
        # Cleanup process
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Cleanup generated files
        for file_to_remove in cleanup_files:
            try:
                Path(file_to_remove).unlink(missing_ok=True)
            except OSError as e:
                print(f"Warning: Could not remove {file_to_remove}: {e}")