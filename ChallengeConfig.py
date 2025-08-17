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
    def load_config(config_path: Optional[Path] = None, config_file:str = "challenge.json") -> Dict[str, Any]:
        """Load config file with proper error handling"""
        default_config = {
            "problem_title": "Problem",
            "challenge_folder": "Challenge",
            "challenge_id": "Challenge",
            "problem_folder": "Problem{:02d}",
            "solution_pattern": "ChallengeProblem_{:02d}.{}",
            "challenge_header": "Challenge",
            "plot_color": "#CE7004"
        }

        # If no path provided, look in current directory
        if config_path is None:
            config_path = Path(config_file)
        # If a directory was provided, look for challenge.json inside it
        elif config_path.is_dir():
            config_path = config_path / config_file

        try:
            if config_path.is_file():
                with config_path.open('r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults
                    return {**default_config, **user_config}
        except (PermissionError, json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"Warning: Couldn't load config ({type(e).__name__}), using defaults")

        return default_config

    def _validate_config(self):
        required_fields = [
            'problem_title',
            'challenge_folder',
            'challenge_id',
            'problem_folder',
            'solution_pattern',
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
        return self.config_data['solution_pattern'].format(
            challenge_folder=self.config_data['challenge_folder'],
            problem_no=problem_no,
            lang=lang
        )

    def get_property(self, property) -> str:
        """Get display title for problems"""
        return self.config_data.get(property, None)

