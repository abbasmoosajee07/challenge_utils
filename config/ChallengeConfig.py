import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Dict, Any

class ChallengeConfig:

    def __init__(self, config_path: Optional[Path] = None, config_file:str = "challenge.json"):
        self.config_path = config_path
        self.config_file = config_file
        self.config_data = self.load_config(config_path, config_file)
        self._validate_config()

    @staticmethod
    def load_config(config_path: Optional[Path] = None, config_file: str = None) -> Dict[str, Any]:
        """Load user config if available, otherwise fall back to default config.
        Raises an error if neither can be loaded."""

        # Location of bundled default config
        default_config_path = Path(__file__).parent / "default_config.json"

        # 1. Try to load user config if provided
        if config_path is not None and config_file is not None:
            if config_path.is_dir():
                config_path = config_path / config_file
            if config_path.is_file():
                try:
                    with config_path.open("r", encoding="utf-8") as f:
                        return json.load(f)
                except (PermissionError, json.JSONDecodeError, UnicodeDecodeError) as e:
                    raise RuntimeError(f"Failed to load user config: {type(e).__name__} - {e}")

        # 2. Try to load default config
        if not default_config_path.is_file():
            raise FileNotFoundError(f"Default config file not found: {default_config_path}")
        try:
            with default_config_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (PermissionError, json.JSONDecodeError, UnicodeDecodeError) as e:
            raise RuntimeError(f"Failed to load default config: {type(e).__name__} - {e}")

    def _validate_config(self):
        required_fields = [
            'challenge_id',
            'problem_title',
            'challenge_folder',
            'problem_folder',
            'solution_file',
            'challenge_header',
            'plot_color'
        ]
        for field in required_fields:
            if field not in self.config_data:
                raise ValueError(f"Missing required config field: {field}")

    def get_problem_folder(self, problem_no: int) -> str:
        """Generate problem folder name from pattern"""
        return self.config_data['problem_folder'].format(problem_no=problem_no)

    def get_solution_filename(self, problem_no: int, lang: str) -> str:
        """Generate solution filename from pattern"""
        return self.config_data['solution_file'].format(
            challenge_folder=self.config_data['challenge_folder'],
            problem_no=problem_no,
            lang=lang
        )

    def get_property(self, property) -> str:
        """Get display title for problems"""
        return self.config_data.get(property, None)

