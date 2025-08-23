import time
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Set
import os

class Language_Support:
    """A class to manage supported programming languages and their execution configurations."""

    def __init__(self, file_path: str = "dummy.txt", exe_path: str = "dummy.exe", input_method: str = ""):
        """
        Initialize the language configuration with file paths and input method.

        Args:
            file_path: Path to the source code file (default: dummy.txt)
            exe_path: Path to the compiled executable (for compiled languages) (default: dummy.exe)
            input_method: Method for providing input ('arg' or other)
        """
        self.file_path = file_path
        self.exe_path = exe_path
        self.input_method = input_method
        self._initialize_language_config()

    @property
    def supported_languages(self) -> List[str]:
        """Return list of supported language extensions."""
        return ["py", "jl", "rb", "js", "c", "rs", "java", "cpp", "hs", "go"]

    @property
    def all_languages(self) -> List[str]:
        """Return list of all available language extensions."""
        return list(self.language_config.keys())

    @property
    def TEMPLATE_PATHS(self) -> Dict[str, Tuple[str, str]]:
        """Return template paths for different languages."""
        return {
            "c": ("c_template.c", "c"),
            "js": ("js_template.js", "js"),
            "go": ("go_template.go", "go"),
            "cpp": ("cpp_template.cpp", "cpp"),
            "txt": ("txt_template.txt", "txt"),
            "ruby": ("ruby_template.rb", "rb"),
            "rust": ("rust_template.rs", "rs"),
            "java": ("java_template.java", "java"),
            "julia": ("julia_template.jl", "jl"),
            "python": ("python_template.py", "py"),
            "haskell": ("haskell_template.hs", "hs"),
        }

    def _initialize_language_config(self) -> None:
        """Initialize the language configuration dictionary."""
        # Use dummy paths for initialization to avoid empty path errors
        dummy_file = Path(self.file_path)
        dummy_exe = Path(self.exe_path)

        self.language_config = {
            # Interpreted languages (direct execution)
            '.py': {
                'run': ['python', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['python', '--version']
            },
            '.rb': {
                'run': ['ruby', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['ruby', '--version']
            },
            '.jl': {
                'run': ['julia', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['julia', '--version']
            },
            '.js': {
                'run': ['node', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['node', '--version']
            },
            '.ts': {
                'run': ['ts-node', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['ts-node', '--version']
            },
            '.pl': {
                'run': ['perl', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['perl', '--version']
            },
            '.php': {
                'run': ['php', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['php', '--version']
            },
            '.lua': {
                'run': ['lua', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['lua', '-v']
            },
            '.r': {
                'run': ['Rscript', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['Rscript', '--version']
            },
            '.sh': {
                'run': ['bash', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['bash', '--version']
            },
            '.ps1': {
                'run': ['pwsh', '-File', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['pwsh', '--version']
            },
            '.go': {
                'run': ['go', 'run', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['go', 'version']
            },

            # Compiled languages (require compilation step)
            '.c': {
                'compile': ['gcc', str(dummy_file), '-o', str(dummy_exe)],
                'run': [str(dummy_exe)],
                'input_method': self.input_method,
                'cleanup': [str(dummy_exe)],
                'tool_check': ['gcc', '--version']
            },
            '.cpp': {
                'compile': ['g++', str(dummy_file), '-o', str(dummy_exe)],
                'run': [str(dummy_exe)],
                'input_method': 'arg',
                'cleanup': [str(dummy_exe)],
                'tool_check': ['g++', '--version']
            },
            '.java': {
                'compile': ['javac', str(dummy_file)],
                'run': ['java', '-cp', str(dummy_file.parent), dummy_file.stem],
                'input_method': 'arg',
                'cleanup': [str(dummy_file.with_suffix('.class'))],
                'tool_check': ['javac', '-version']
            },
            '.rs': {
                'compile': ['rustc', str(dummy_file), '-o', str(dummy_exe)],
                'run': [str(dummy_exe)],
                'input_method': 'arg',
                'cleanup': [str(dummy_exe)],
                'tool_check': ['rustc', '--version']
            },

            # Other languages
            '.scala': {
                'run': ['scala', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['scala', '-version']
            },
            '.swift': {
                'run': ['swift', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['swift', '--version']
            },
            '.kt': {
                'run': ['kotlin', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['kotlin', '-version']
            },
            '.hs': {
                'run': ['runhaskell', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['ghc', '--version']
            },
            '.ml': {
                'run': ['ocaml', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['ocaml', '--version']
            },
            '.clj': {
                'run': ['clojure', str(dummy_file)],
                'input_method': self.input_method,
                'tool_check': ['clojure', '--version']
            },
        }

    def get_tool_path(self, command_name: str) -> str:
        """Get the full path to a command executable"""
        try:
            # Try 'where' command (Windows)
            if os.name == 'nt':
                result = subprocess.run(['where', command_name], capture_output=True, text=True, timeout=5)
            else:
                # Try 'which' command (Unix/Linux/Mac)
                result = subprocess.run(['which', command_name], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                paths = result.stdout.strip().split('\n')
                return paths[0] if paths else "Not found"
            return "Not found"
        except subprocess.TimeoutExpired:
            return "Timeout finding path"
        except Exception:
            return "Error finding path"

    def check_tool(self, language_ext: str, check_all: bool = False) -> Tuple[str, str, str]:
        """
        Check if a tool for a specific language is available.
        Args:
            language_ext: The language extension (e.g., '.py', '.js')
            check_all: If False, only check supported languages
        Returns:
            Tuple of (status, version, path)
        """
        # If not checking all languages and this language isn't supported, skip
        if not check_all and language_ext[1:] not in self.supported_languages:
            return "[SKIP]", "Skipped (not supported)", "N/A"

        if language_ext not in self.language_config:
            return "[UNK]", "Unknown language", "N/A"

        config = self.language_config[language_ext]
        if 'tool_check' not in config:
            return "[N/A]", "No tool check configured", "N/A"

        cmd = config['tool_check']
        tool_name = cmd[0]

        try:
            # Get the tool path
            tool_path = self.get_tool_path(tool_name)

            # Check version
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip() or result.stderr.strip()
                status = "[OK]"
                status_text = version.split('\n')[0]  # Take first line only
            else:
                status = "[NO]"
                status_text = "Not available"

            return status, status_text, tool_path

        except FileNotFoundError:
            return "[NO]", "Not found", self.get_tool_path(tool_name)
        except subprocess.TimeoutExpired:
            return "[TO]", "Timeout checking version", self.get_tool_path(tool_name)
        except Exception as e:
            return "[ERR]", f"Error: {str(e)}", self.get_tool_path(tool_name)

    def check_all_tools(self, check_all_languages: bool = False) -> None:
        """
        Check all available tools, optionally filtering to only supported languages.

        Args:
            check_all_languages: If True, check all languages; if False, only check supported ones
        """
        print("Checking available tools:")
        print("=" * 80)

        # Get languages to check
        if check_all_languages:
            languages_to_check = self.all_languages
            print("Checking ALL available languages:")
        else:
            languages_to_check = [f".{lang}" for lang in self.supported_languages]
            print("Checking SUPPORTED languages only:")

        print(f"Languages: {', '.join([lang[1:] for lang in languages_to_check])}")
        print()

        max_lang_len = max(len(lang[1:]) for lang in languages_to_check)  # Remove dot for display

        results = []
        for lang_ext in sorted(languages_to_check):
            status, version, path = self.check_tool(lang_ext, check_all_languages)
            lang_name = lang_ext[1:]  # Remove dot for display
            results.append((lang_name, status, version, path))

        # Print results
        for lang_name, status, version, path in results:
            print(f"{status} {lang_name:<{max_lang_len}} : {version}")
            if path != "N/A":
                print(f"  {' ' * len(status)} {' ' * max_lang_len}   Path: {path}")
            print()

        print("=" * 80)

        # Summary
        total = len(results)
        available = sum(1 for _, status, _, _ in results if status == "[OK]")
        skipped = sum(1 for _, status, _, _ in results if status == "[SKIP]")

        print(f"Summary: {available}/{total - skipped} available, {skipped} skipped")
        if not check_all_languages and skipped > 0:
            print("(Skipped languages are not in supported list)")

        # Legend
        print("\nLegend:")
        print("[OK]   - Tool is available")
        print("[NO]   - Tool not found/not available")
        print("[SKIP] - Language not in supported list")
        print("[TO]   - Timeout occurred")
        print("[ERR]  - Error occurred")
        print("[UNK]  - Unknown language")
        print("[N/A]  - No tool check configured")

# Example usage
if __name__ == "__main__":
    # Initialize language support with dummy file paths
    lang_support = Language_Support("dummy.txt", "dummy.exe")

    print("=== CHECKING SUPPORTED LANGUAGES ONLY ===")
    lang_support.check_all_tools(check_all_languages=False)

    print("\n" + "="*80 + "\n")

