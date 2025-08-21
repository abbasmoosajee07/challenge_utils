import sys, os, time
from pathlib import Path
from typing import Optional, Dict, Any
from ..core.SupportedLangs import Language_Support
from ..config.ChallengeConfig import ChallengeConfig

class ScriptBuilder:
    TEMPLATE_PATHS = Language_Support.TEMPLATE_PATHS

    def __init__(self, author: str, challenge_dir: Path, config_file: str):
        self.author = author
        self.challenge_dir = Path(challenge_dir)
        self.config = ChallengeConfig(self.challenge_dir, config_file)
        self._challenge_header_printed = False  # Track if we printed challenge folder

    def _log(self, path: Path, message: str):
        """Print path relative to challenge folder after printing challenge folder once."""
        if not self._challenge_header_printed:
            print(f"[Challenge Folder] {self.challenge_dir}")
            self._challenge_header_printed = True
        relative_path = path.relative_to(self.challenge_dir)
        print(f"[{message}] {relative_path}")

    def _generate_header(self, prob_no: int) -> str:
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

    def _create_problem_folder(self, prob_no: int) -> Path:
        formatted_prob = self.config.get_problem_folder(prob_no)
        problem_dir = self.challenge_dir / formatted_prob
        if not problem_dir.exists():
            problem_dir.mkdir(parents=True, exist_ok=True)
            self._log(problem_dir, "Folder Created")
        else:
            self._log(problem_dir, "Folder Exists")
        return problem_dir

    def _create_text_files(self, prob_no: int, txt_files: int) -> str:
        base_name = self.config.get_property("text_input").format(problem_no=prob_no)
        selected_file = None
        count = max(1, txt_files)

        for i in range(1, count + 1):
            suffix = "" if txt_files <= 1 else f"_p{i}"
            file_name = f"{base_name}{suffix}.txt"
            file_path = self.problem_dir / file_name

            if not file_path.exists():
                file_path.write_text("", encoding="utf-8")
                self._log(file_path, "Text File Created")
            else:
                self._log(file_path, "Text File Exists")

            if selected_file is None:
                selected_file = file_name

        return selected_file

    def _script_properties(self, prob_no: int, language: str, text_file: str):
        script_template, ext = self.TEMPLATE_PATHS.get(language.lower(), ("", "txt"))
        file_name = self.config.get_solution_filename(prob_no, ext)
        template_path = Path("challenge_utils/templates") / script_template
        template_content = template_path.read_text(encoding="utf-8")

        header = self._generate_header(prob_no)
        filled_content = template_content.format(
            header_text=header,
            file_name=file_name.split(".")[0],
            text_placeholder=text_file
        )
        return filled_content, self.problem_dir / file_name

    def create_files(self, prob_no: int, language: str, txt_files: int = 1) -> Path:
        if language.lower() not in self.TEMPLATE_PATHS:
            raise ValueError(f"No template for language: {language}")

        self.problem_dir = self._create_problem_folder(prob_no)
        sel_txt_file = self._create_text_files(prob_no, txt_files)

        script_content, file_path = self._script_properties(prob_no, language, sel_txt_file)
        if file_path.exists():
            self._log(file_path, "Script Skipped")
            return file_path

        file_path.write_text(script_content, encoding="utf-8")
        self._log(file_path, f"{language} Script Created")
        return file_path
