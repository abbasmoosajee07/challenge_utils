import sys, os, time
from pathlib import Path
from typing import Optional, Dict, Any
from config.ChallengeConfig import ChallengeConfig

class ScriptBuilder:
    TEMPLATE_PATHS = {
        "c": ("c_template.c", "c"),
        "js": ("js_template.js", "js"),
        "txt": ("txt_template.txt", "txt"),
        "ruby": ("ruby_template.rb", "rb"),
        "julia": ("julia_template.jl", "jl"),
        "python": ("python_template.py", "py"),
    }

    def __init__(self, author: str, challenge_dir: Path, config_file: str):
        self.author = author
        self.challenge_dir = Path(challenge_dir)
        self.config = ChallengeConfig(self.challenge_dir, config_file)

    def _generate_header(self, prob_no: int) -> str:
        """Generate a standard header for solution scripts."""
        current_time = time.localtime()
        header_template = self.config.get_property("script_header")

        context = {
            "author": self.author,
            "problem_no": prob_no,
            "id": self.config.get_property("challenge_id"),
            "current_time": current_time,
            "month": time.strftime("%B", current_time),
        }

        return header_template.format(**context)

    def _create_problem_folder(self, prob_no: int) -> str:
        formatted_prob = self.config.get_problem_folder(prob_no)
        problem_dir = self.challenge_dir / formatted_prob
        problem_dir.mkdir(parents=True, exist_ok=True)
        return problem_dir

    def _create_text_files(self, prob_no: int, txt_files: int) -> str:
        base_name = self.config.get_property("text_input").format(problem_no=prob_no)

        selected_file = None
        count = max(1, txt_files)  # Ensure at least one file

        for i in range(1, count + 1):
            suffix = "" if txt_files <= 1 else f"_p{i}"
            file_name = f"{base_name}{suffix}.txt"
            file_path = self.problem_dir / file_name

            if not file_path.exists():
                file_path.write_text("", encoding="utf-8")

            if selected_file is None:
                selected_file = file_name

        return selected_file

    def _script_properties(self, prob_no: int, language: str, text_file: str) -> None:
        """Fill a template with header and write the script file."""
        script_template, ext = self.TEMPLATE_PATHS.get(language.lower(), ("", "txt"))
        file_name = self.config.get_solution_filename(prob_no, ext)

        template_path = "challenge_utils/templates" / Path(script_template)
        template_content = template_path.read_text(encoding="utf-8")

        header = self._generate_header(prob_no)
        filled_content = template_content.format(
            header_text=header,
            text_placeholder = text_file
        )
        return filled_content, self.problem_dir / file_name

    def create_files(self, prob_no: int, language: str, txt_files: int = 1) -> Path:
        """Create a solution script for the given problem and language."""
        if language not in self.TEMPLATE_PATHS:
            raise ValueError(f"No template for language: {language}")

        self.problem_dir = self._create_problem_folder(prob_no)

        sel_txt_file = self._create_text_files(prob_no, txt_files)

        script_content, file_path = self._script_properties(prob_no, language, sel_txt_file)
        if file_path.exists():
            print(f"File already exists: {file_path}")
            return file_path

        file_path.write_text(script_content, encoding="utf-8")
        print(f"Created {language} script: {file_path}")
        return file_path
