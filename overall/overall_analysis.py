import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import re

class CodePerformanceAnalyzer:
    """
    A class to analyze performance metrics across coding challenges.
    Generic enough to handle various coding challenge formats.
    """
    
    # Constants for better maintainability
    DEFAULT_RESULTS_PATTERN = "*_results.txt"
    TIME_THRESHOLD_MS = 15000  # Threshold for slow problems (15 seconds)
    MILLISECONDS_TO_SECONDS = 1/1000  # Conversion factor
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize the analyzer with a repository path.
        
        Args:
            repo_path: Path to the repository root. If None, will attempt to auto-detect.
        """
        self.repo_path = repo_path or self.get_repository_path()
        self.data = pd.DataFrame()
        self.analysis_results = {}
        
    @staticmethod
    def get_repository_path(current_file: Optional[str] = None) -> Path:
        """
        Returns the absolute Path to the repository's root directory.
        
        Args:
            current_file: The __file__ variable from the calling script
            
        Returns:
            Path object pointing to the repository root
        """
        if current_file:
            current_file_path = Path(current_file).resolve()
            repo_path = current_file_path.parent.parent
        else:
            # Fallback: try to find the repository by looking for common patterns
            current_dir = Path.cwd()
            # Look for a parent directory that contains multiple challenge folders
            for parent in [current_dir] + list(current_dir.parents):
                if any((parent / "analysis").exists() for item in parent.iterdir() if item.is_dir()):
                    repo_path = parent
                    break
            else:
                repo_path = current_dir
                
        return repo_path
    
    def parse_performance_file(self, file_path: Path, challenge_id: str) -> List[Dict[str, Any]]:
        """
        Parses a single performance results file.
        
        Args:
            file_path: Path to the results file
            challenge_id: The identifier for this challenge set
            
        Returns:
            List of dictionaries containing parsed data
        """
        try:
            with file_path.open('r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Warning: File not found: {file_path}")
            return []
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []
        
        # Find table boundaries
        table_boundaries = []
        for i, line in enumerate(lines):
            if re.match(r'^-+$', line.strip()):  # Match lines with only dashes
                table_boundaries.append(i)
        
        if len(table_boundaries) < 2:
            print(f"Warning: Invalid table format in file: {file_path}")
            return []
        
        # Extract table content
        data = []
        table_start, table_end = table_boundaries[0] + 1, table_boundaries[1]
        
        for line in lines[table_start:table_end]:
            line = line.strip()
            if not line or line.startswith('-'):
                continue
            
            # Split on whitespace but preserve language names with spaces
            parts = line.split()
            if len(parts) < 10:  # Minimum expected columns
                continue
            
            try:
                # Extract fixed position values
                problem_num = int(parts[0])
                avg_time = float(parts[1])
                std_time = float(parts[2])
                rel_time = float(parts[3].strip('%'))
                avg_mb = float(parts[4])
                std_mb = float(parts[5])
                rel_mb = float(parts[6].strip('%'))
                file_size = float(parts[-2])  # Second to last
                lines_count = int(parts[-1])  # Last
                
                # Language might be one or multiple words
                lang_parts = parts[7:-2]
                language = ' '.join(lang_parts)
                
                data.append({
                    "Challenge": challenge_id,
                    "Problem": problem_num,
                    "Avg_ms": avg_time,
                    "STD_ms": std_time,
                    "rel_ms": rel_time,
                    "Avg_mb": avg_mb,
                    "STD_mb": std_mb,
                    "rel_mb": rel_mb,
                    "Lang": language,
                    'Size_kb': file_size,
                    "Lines": lines_count
                })
            except (ValueError, IndexError) as e:
                print(f"Warning: Error parsing line in {file_path}: {line}")
                continue
        
        return data
    
    def find_results_files(self, pattern: str = DEFAULT_RESULTS_PATTERN) -> List[Tuple[Path, str]]:
        """
        Recursively finds all results files in the repository.
        
        Args:
            pattern: Glob pattern to match results files
            
        Returns:
            List of tuples containing (file_path, challenge_id)
        """
        results_files = []
        
        # Look for challenge folders (can be years, names, or any identifier)
        for challenge_path in self.repo_path.iterdir():
            if challenge_path.is_dir():
                challenge_id = challenge_path.name
                
                # Search for results files in any subdirectory
                for results_file in challenge_path.rglob(pattern):
                    results_files.append((results_file, challenge_id))
        
        return results_files
    
    def load_data(self, pattern: str = DEFAULT_RESULTS_PATTERN) -> pd.DataFrame:
        """
        Loads and combines performance data from all results files.
        
        Args:
            pattern: Glob pattern to match results files
            
        Returns:
            DataFrame containing all parsed performance data
        """
        if not self.repo_path.exists():
            print(f"Error: Repository folder does not exist: {self.repo_path}")
            return pd.DataFrame()

        # Find all results files
        results_files = self.find_results_files(pattern)
        
        if not results_files:
            print("Warning: No results files found")
            return pd.DataFrame()
        
        # Parse all files
        all_data = []
        for file_path, challenge_id in results_files:
            print(f"Processing: {file_path}")
            challenge_data = self.parse_performance_file(file_path, challenge_id)
            all_data.extend(challenge_data)
        
        self.data = pd.DataFrame(all_data)
        return self.data
    
    def analyze(self) -> Dict[str, pd.DataFrame]:
        """
        Analyzes the performance data and returns summary statistics.
        
        Returns:
            Dictionary with various summary statistics
        """
        if self.data.empty:
            print("Warning: No data to analyze")
            return {}
        
        # Find slowest and fastest problems
        slowest = self.data.nlargest(5, 'Avg_ms')
        fastest = self.data.nsmallest(5, 'Avg_ms')
        
        # Summary by language
        lang_summary = self.data.groupby('Lang').agg({
            'Avg_ms': ['count', 'mean', 'median', 'max'],
            'Avg_mb': ['mean', 'max']
        }).round(2)
        
        # Summary by challenge
        challenge_summary = self.data.groupby('Challenge').agg({
            'Avg_ms': ['count', 'mean', 'median', 'sum'],
            'Avg_mb': ['mean', 'max', 'sum']
        }).round(2)
        
        self.analysis_results = {
            'slowest': slowest,
            'fastest': fastest,
            'by_language': lang_summary,
            'by_challenge': challenge_summary
        }
        
        return self.analysis_results
    
    def print_summary(self):
        """Prints a formatted summary of the analysis."""
        if not self.analysis_results:
            print("No analysis results available. Run analyze() first.")
            return
        
        print("\n" + "="*60)
        print("CODE CHALLENGE PERFORMANCE ANALYSIS SUMMARY")
        print("="*60)
        
        print("\nSLOWEST PROBLEMS (Top 5):")
        print(self.analysis_results['slowest'][['Challenge', 'Problem', 'Avg_ms', 'STD_ms', 'Avg_mb', 'Lang']].to_string(index=False))
        
        print("\nFASTEST PROBLEMS (Top 5):")
        print(self.analysis_results['fastest'][['Challenge', 'Problem', 'Avg_ms', 'STD_ms', 'Avg_mb', 'Lang']].to_string(index=False))
        
        print("\nSUMMARY BY LANGUAGE:")
        print(self.analysis_results['by_language'].to_string())
        
        print("\nSUMMARY BY CHALLENGE:")
        print(self.analysis_results['by_challenge'].to_string())
    
    def create_summary_plot(self, output_dir: Path) -> Optional[pd.DataFrame]:
        """
        Creates and saves a visualization of challenge performance.
        
        Args:
            output_dir: Directory to save the plot
            
        Returns:
            Summary DataFrame if successful, None otherwise
        """
        if self.data.empty:
            print("Warning: No data to plot")
            return None
            
        # Summary by challenge
        summary = self.data.groupby('Challenge').agg(
            Total_Time_ms=('Avg_ms', 'sum'),
            Average_Time_ms=('Avg_ms', 'mean'),
            Median_Time_ms=('Avg_ms', 'median'),
            Total_Memory_mb=('Avg_mb', 'sum'),
        ).reset_index()

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Normalize memory usage for color mapping
        norm = plt.Normalize(summary['Total_Memory_mb'].min(), summary['Total_Memory_mb'].max())
        colors = plt.cm.viridis(norm(summary['Total_Memory_mb']))
        
        # Convert time to seconds for more readable axis
        total_time_seconds = summary['Total_Time_ms'] * self.MILLISECONDS_TO_SECONDS
        
        # Create bar plot
        bars = ax.bar(
            range(len(summary['Challenge'])), 
            total_time_seconds, 
            color=colors, 
            edgecolor='black', 
            linewidth=0.5,
            alpha=0.8,
            zorder=2
        )
        
        # Add color bar for memory usage
        sm = plt.cm.ScalarMappable(cmap='viridis', norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label('Total Memory Usage (MB)', fontsize=12)
        
        # Customize plot
        ax.set_title('Code Challenges: Performance Summary', fontsize=16, pad=20)
        ax.set_xlabel('Challenge Set', fontsize=12)
        ax.set_ylabel('Total Execution Time (seconds)', fontsize=12)
        ax.set_xticks(range(len(summary['Challenge'])))
        ax.set_xticklabels(summary['Challenge'], rotation=45)
        
        # Add grid for better readability
        ax.grid(visible=True, which='major', color='grey', axis='y', 
                linestyle='--', linewidth=0.7, alpha=0.7, zorder=1)
        
        # Add value labels on top of bars
        for i, (challenge, value) in enumerate(zip(summary['Challenge'], total_time_seconds)):
            ax.text(i, value + max(total_time_seconds)*0.01, 
                    f'{value:.1f}s', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Save the plot
        output_dir.mkdir(parents=True, exist_ok=True)
        plot_path = output_dir / 'performance_summary.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        print(f"Plot saved to {plot_path}")
        
        plt.show()
        return summary
    
    def export_slow_problems(self, output_dir: Path, 
                            threshold_ms: int = TIME_THRESHOLD_MS) -> Path:
        """
        Exports problems exceeding a time threshold to a file.
        
        Args:
            output_dir: Directory to save the output file
            threshold_ms: Time threshold in milliseconds
            
        Returns:
            Path to the exported file
        """
        if self.data.empty:
            print("Warning: No data to export")
            return Path()
            
        slow_problems = self.data[self.data['Avg_ms'] >= threshold_ms].copy()
        
        # Convert time to seconds for readability
        slow_problems['Avg_seconds'] = slow_problems['Avg_ms'] * self.MILLISECONDS_TO_SECONDS
        slow_problems = slow_problems[['Challenge', 'Problem', 'Avg_seconds', 'Avg_mb', 'Lang']]
        
        # Sort by time (descending)
        slow_problems = slow_problems.sort_values('Avg_seconds', ascending=False)
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"slow_problems_over_{threshold_ms//1000}s.txt"
        
        # Save to file
        slow_problems.to_csv(output_file, sep="\t", index=False, float_format="%.2f")
        
        print(f"Exported {len(slow_problems)} slow problems to {output_file}")
        return output_file
    
    def run_full_analysis(self, output_dir: Optional[Path] = None):
        """
        Runs the complete analysis pipeline.
        
        Args:
            output_dir: Directory to save outputs. If None, uses default location.
        """
        if output_dir is None:
            output_dir = Path(__file__).parent / "performance_analysis_output"
        
        print(f"Starting analysis of repository: {self.repo_path}")
        
        # Load data
        self.load_data()
        
        if self.data.empty:
            print("No data found. Exiting.")
            return
        
        print(f"Loaded {len(self.data)} performance records")
        
        # Analyze the data
        self.analyze()
        self.print_summary()
        
        # Create visualizations and exports
        self.create_summary_plot(output_dir)
        self.export_slow_problems(output_dir)
        
        print(f"\nAnalysis complete. Results saved to {output_dir}")


# Example usage and demonstration
if __name__ == "__main__":
    # Create analyzer instance
    analyzer = CodePerformanceAnalyzer()
    
    # Run full analysis
    analyzer.run_full_analysis()
    
    # Alternatively, use step-by-step:
    # analyzer.load_data()
    # analyzer.analyze()
    # analyzer.print_summary()
    # analyzer.create_summary_plot(Path("output"))
    # analyzer.export_slow_problems(Path("output"))