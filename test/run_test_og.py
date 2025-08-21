import subprocess
import glob
import json
import time
import re
import psutil
import numpy as np
import pandas as pd
import matplotlib
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.cm import ScalarMappable
from typing import Dict, List, Tuple, Optional, Dict, Any
matplotlib.use('TkAgg')  # or 'Qt5Agg' if you have PyQt5 installed

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

class ResultsProcessor:
    """Combines performance results table generation and visualization plotting"""

    def __init__(self, challenge_id, problem_title):
        self.table_lines = []
        self.challenge_id = challenge_id
        self.problem_title = problem_title

    # Table generation methods
    def generate_table(self, file_info, times_taken, peak_memory_usage, iterations, challenge):
        """Create results table and DataFrame"""
        stats = self._calculate_stats(times_taken, peak_memory_usage)
        
        # Initialize containers for both outputs
        self.table_lines = []
        df_data = []
        total_lines, total_size = 0, 0.0
        
        # Build headers
        headers = [self.problem_title, "Avg(ms)", "STD(ms)", "Time%", 
                  "Avg(MB)", "STD(MB)", "Mem%", 
                  "Lang", "Size(kB)", "Lines"]
        
        # Table header
        self.table_lines.append(
            "{:<8} {:<10} {:<10} {:<8} {:<10} {:<10} {:<8} {:<10} {:<10} {:<6}".format(*headers)
        )
        self.table_lines.append("-" * 95)
        
        # Process each problem
        for problem in sorted(k for k in stats.keys() if k != 'total'):
            s = stats[problem]
            time_pct = (s['avg_time'] / stats['total']['time'] * 100) if stats['total']['time'] > 0 else 0
            mem_pct = (s['avg_mem'] / stats['total']['memory'] * 100) if stats['total']['memory'] > 0 else 0
            
            lang, lines, size = file_info.get(problem, ("", 0, 0.0))
            total_lines += lines
            total_size += size
            
            # Add to table lines
            self.table_lines.append(
                "{:<8} {:<10.2f} {:<10.2f} {:<8.2f} {:<10.2f} {:<10.2f} {:<8.2f} {:<10} {:<10.2f} {:<6}"
                .format(problem, s['avg_time'], s['std_time'], time_pct,
                        s['avg_mem'], s['std_mem'], mem_pct,
                        lang, size, lines)
            )
            
            # Add to DataFrame data
            df_data.append([
                problem, s['avg_time'], s['std_time'], time_pct,
                s['avg_mem'], s['std_mem'], mem_pct,
                lang, size, lines
            ])
        
        # Add totals
        self.table_lines.extend([
            "-" * 95,
            "{:<8} {:<10.2f} {:<10.2f} {:<8.2f} {:<10.2f} {:<10.2f} {:<8.2f} {:<10} {:<10.2f} {:<6}"
            .format("Total", stats['total']['time'], stats['total']['time_std'], 100,
                    stats['total']['memory'], stats['total']['memory_std'], 100,
                    "", total_size, total_lines),
            f"\nChallenge: {challenge}, Iterations: {iterations}"
        ])
        
        # Add totals to DataFrame
        df_data.append([
            "Total", stats['total']['time'], stats['total']['time_std'], 100,
            stats['total']['memory'], stats['total']['memory_std'], 100,
            "", total_size, total_lines
        ])
        
        # Create DataFrame
        df = pd.DataFrame(df_data, columns=[
            self.problem_title, "Avg(ms)", "STD(ms)", "Time%",
            "Avg(MB)", "STD(MB)", "Memory %",
            "Lang", "Size(kB)", "Lines"
        ])
        
        return df

    def _calculate_stats(self, times_taken, peak_memory_usage):
        """Calculate performance statistics"""
        stats = {}
        total_time = total_memory = 0
        
        for problem in times_taken:
            times = times_taken[problem]
            mems = peak_memory_usage.get(problem, [])
            
            avg_time = np.mean(times) if times else 0
            std_time = np.std(times) if times else 0
            avg_mem = np.mean(mems) if mems else 0
            std_mem = np.std(mems) if mems else 0
            
            stats[problem] = {
                'avg_time': avg_time,
                'std_time': std_time,
                'avg_mem': avg_mem,
                'std_mem': std_mem
            }
            
            total_time += avg_time
            total_memory += avg_mem
            
        stats['total'] = {
            'time': total_time,
            'memory': total_memory,
            'time_std': sum(s['std_time'] for s in stats.values()),
            'memory_std': sum(s['std_mem'] for s in stats.values())
        }
        
        return stats

    def save_table_to_file(self, file_path: Path):
        """Save table to text file"""
        with file_path.open('w') as f:
            f.write("\n".join(self.table_lines))
        print(f"Results table saved to {file_path}")

    # Plotting methods
    def generate_plot(self, df: pd.DataFrame, challenge: str,
                    iterations: int, save_dir: Path, center_color: str = "#4CAF50",
                    scale: str = 'linear'):
        """Main plotting function"""
        # Data preparation
        df = df[df[self.problem_title] != 'Total']
        problems = pd.to_numeric(df[self.problem_title])
        avg_times = df['Avg(ms)']
        std_devs = df['STD(ms)']
        avg_mems = df['Avg(MB)']
        rel_memory = df['Memory %']

        # Create plot elements
        fig, ax = self._setup_figure()
        bars = self._create_bars(ax, problems, avg_times, center_color, rel_memory)
        self._add_annotations(ax, bars, df)
        self._configure_axes(ax, problems, avg_times, scale)
        self._highlight_extremes(ax, bars, problems, avg_times)
        self._add_reference_lines(ax, avg_times)
        self._add_error_bars(ax, problems, avg_times, std_devs)
        self._add_legends(ax, challenge, iterations, avg_times, avg_mems)
        self._add_colorbar(fig, ax, center_color, rel_memory)

        # Finalize and save
        plt.tight_layout()
        plot_path = save_dir / f"{self.challenge_id}_{scale}_plot.png"
        plt.savefig(plot_path, bbox_inches='tight')
        plt.show()

    # Plotting helper methods (kept small for debugging)
    @staticmethod
    def generate_gradient_around_color(center_color, num_steps=10):
        """Create a gradient around the given center color."""
        center_rgb = mcolors.hex2color(center_color)
        lighter_colors = [tuple(min(1, c + i * 0.05) for c in center_rgb) for i in range(num_steps)]
        darker_colors = [tuple(max(0, c - i * 0.05) for c in center_rgb) for i in range(num_steps)]
        # Combine them to form a full gradient (darker -> center -> lighter)
        full_gradient = darker_colors[::-1] + [center_rgb] + lighter_colors
        return full_gradient[::-1]

    def _setup_figure(self):
        """Initialize figure with original dimensions"""
        return plt.subplots(figsize=(15.6, 15.6 * 9 / 16))

    def _create_bars(self, ax, problems, avg_times, center_color, rel_memory):
        """Create colored bars"""
        gradient = self.generate_gradient_around_color(center_color)
        cmap = mcolors.LinearSegmentedColormap.from_list("custom_gradient", gradient)
        norm = mcolors.Normalize(vmin=min(rel_memory), vmax=max(rel_memory))
        bar_colors = [cmap(norm(p)) for p in rel_memory]
        return ax.bar(problems, avg_times, color=bar_colors, zorder=3, alpha=0.95)

    def _add_annotations(self, ax, bars, df):
        """Add bar annotations"""
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.annotate(
                f"({df['Lang'].iloc[i]} | {df['Size(kB)'].iloc[i]:.2f} kB) \n PM = {df['Avg(MB)'].iloc[i]:.1f} MB",
                xy=(bar.get_x() + bar.get_width()/2, height),
                xytext=(bar.get_x() - 0.3, height * 1.15),
                arrowprops=dict(facecolor='black', arrowstyle='->'),
                fontsize=7, color='black', rotation=90, zorder=5
            )

    def _configure_axes(self, ax, problems, avg_times, scale):
        """Configure axes"""
        ax.set_yscale(scale)
        ax.set_xticks(problems)
        ax.set_xticklabels([f'{self.problem_title} {int(p)}' for p in problems], rotation=45, ha='right')
        ax.set_ylabel(f"({scale.capitalize()} Scale) Average Time (ms)", fontsize=14)
        ax.grid(True, which='major', axis='y', linestyle='--', linewidth=0.8, alpha=0.8)
        ax.minorticks_on()
        ax.grid(True, which='minor', axis='y', linestyle=':', linewidth=0.6, alpha=0.6)
        
        if scale == 'linear':
            ax.set_ylim(0, max(avg_times) * 1.425)
        else:
            ax.set_ylim(max(min(avg_times) * 0.9, 1e-2), max(avg_times) * 3.2)

    def _highlight_extremes(self, ax, bars, problems, avg_times):
        """Highlight min/max bars"""
        max_idx, min_idx = np.argmax(avg_times), np.argmin(avg_times)
        bars[max_idx].set_edgecolor('red')
        bars[max_idx].set_linewidth(2)
        bars[min_idx].set_edgecolor('blue')
        bars[min_idx].set_linewidth(2)
        ax.plot(problems[max_idx], avg_times[max_idx], '-', color='red', 
               label=f"Max: {avg_times[max_idx]/1000:.2f} s", markersize=8, zorder=5)
        ax.plot(problems[min_idx], avg_times[min_idx], '-', color='blue',
               label=f"Min: {avg_times[min_idx]/1000:.2f} s", markersize=8, zorder=5)

    def _add_reference_lines(self, ax, avg_times):
        """Add reference lines"""
        avg = np.mean(avg_times)
        median = np.median(avg_times)
        ax.axhline(avg, color='#008000', linestyle='-', label=f'Average: {avg/1000:.2f} s')
        ax.axhline(median, color='#800080', linestyle='-', label=f'Median: {median/1000:.2f} s')

    def _add_error_bars(self, ax, problems, avg_times, std_devs):
        """Add error bars"""
        ax.errorbar(problems, avg_times, yerr=std_devs, fmt='none', 
                   color='#FFD700', capsize=3, zorder=4)

    def _add_legends(self, ax, challenge, iterations, avg_times, avg_mems):
        """Add complex legend"""
        total_time = np.sum(avg_times)
        total_mem = np.sum(avg_mems)
        
        # Main legend items
        legend_items = ax.legend(loc='upper left', bbox_to_anchor=(0, 1), 
                                fontsize=7, frameon=True, 
                                facecolor='white', edgecolor='black')
        
        # Custom info lines
        custom_lines = [
            plt.Line2D([0], [0], color='white', label=f"Scale: {ax.get_yscale().capitalize()}"),
            plt.Line2D([0], [0], color='white', label=f"Iterations: {iterations}"),
            plt.Line2D([0], [0], color='white', label=f"Peak Memory (PM): {total_mem:.2f} MB"),
            plt.Line2D([0], [0], color='white', label=f"Avg Run Time: {total_time/1000:.2f} s"),
        ]
        
        # Combined legend
        final_legend = ax.legend(
            handles=custom_lines + legend_items.legend_handles,
            loc='upper left', bbox_to_anchor=(0, 1), 
            fontsize=9, frameon=True,
            facecolor='white', edgecolor='black',
            ncol=2
        )
        ax.add_artist(final_legend)
        ax.set_title(f'{challenge}', fontsize=21, fontweight='bold')

    def _add_colorbar(self, fig, ax, center_color, rel_memory):
        """Add colorbar"""
        gradient = self.generate_gradient_around_color(center_color)
        cmap = mcolors.LinearSegmentedColormap.from_list("custom_gradient", gradient)
        norm = mcolors.Normalize(vmin=min(rel_memory), vmax=max(rel_memory))
        cbar = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax)
        cbar.set_label('Relative Percentage of Total Peak Memory (%)', fontsize=12)

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


if __name__ == "__main__":

    base_dir = Path.cwd() / str("test_config")
    script_dir = Path(__file__).parent.resolve()
    selected_dir = script_dir
    config_file = "test_config.json"

    PROBLEMS_TO_RUN = list(range(1, 26))  # Problems 1-25

    analyzer = ChallengeBenchmarks(
        base_dir = selected_dir,
        config_file = config_file,
    )

    results = analyzer.analyze(
        problems_to_run= PROBLEMS_TO_RUN,  # Problems 1-25
        iterations=1,
        save_results=False,
        custom_dir= script_dir / "analysis"
    )

    print("\nAnalysis complete!")
    print(results.head(25))