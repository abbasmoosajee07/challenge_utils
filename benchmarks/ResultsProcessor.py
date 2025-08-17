import numpy as np
import pandas as pd
import matplotlib
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.cm import ScalarMappable
matplotlib.use('TkAgg')  # or 'Qt5Agg' if you have PyQt5 installed

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
