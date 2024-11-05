import os
import glob
from pathlib import Path
import argparse
from collections import defaultdict
import time
from datetime import datetime
import sys

class ProgressLogger:
    def __init__(self, total=None):
        self.total = total
        self.current = 0
        self.start_time = time.time()
        self.last_update = self.start_time
        self.update_interval = 0.1  # seconds

    def update(self, current=None, force=False):
        if current is not None:
            self.current = current
        else:
            self.current += 1

        current_time = time.time()
        if force or (current_time - self.last_update) >= self.update_interval:
            self.last_update = current_time
            self._print_progress()

    def _print_progress(self):
        if self.total:
            percentage = (self.current / self.total) * 100
            progress_bar = self._create_progress_bar(percentage)
            sys.stdout.write(f"\r{progress_bar} {percentage:.1f}% ({self.current}/{self.total})")
        else:
            sys.stdout.write(f"\rProcessed {self.current} files...")
        sys.stdout.flush()

    def _create_progress_bar(self, percentage, width=30):
        filled = int(width * percentage / 100)
        return f"[{'=' * filled}{' ' * (width - filled)}]"

    def finish(self):
        duration = time.time() - self.start_time
        sys.stdout.write("\n")
        return duration

def count_lines(file_path):
    """Count non-empty lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for line in f if line.strip())
    except UnicodeDecodeError:
        # Skip binary files
        return 0
    except Exception as e:
        print(f"\nError reading {file_path}: {e}")
        return 0

def get_total_files(root_dir, include_extensions):
    """Count total files to process for progress tracking."""
    total = 0
    root_path = Path(root_dir)
    for ext in include_extensions:
        total += len(list(root_path.glob(f"**/*{ext}")))
    return total

def analyze_repo(root_dir, exclude_dirs=None, exclude_files=None, include_extensions=None, verbose=False):
    """
    Analyze a repository for lines of code with progress logging.
    """
    print(f"\nStarting analysis at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Repository path: {root_dir}")
    
    if exclude_dirs is None:
        exclude_dirs = ['node_modules', 'dist', 'build', 'venv', '.git', '__pycache__', 'generated']
    
    if exclude_files is None:
        exclude_files = ['*.min.js', '*.min.css', '*.map', '*.pyc', '*.g.dart']
    
    if include_extensions is None:
        include_extensions = ['dart', '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.h', '.css', '.scss']
    
    print("\nConfiguration:")
    print(f"- Excluded directories: {', '.join(exclude_dirs)}")
    print(f"- Excluded file patterns: {', '.join(exclude_files)}")
    print(f"- Included extensions: {', '.join(include_extensions)}")
    
    stats = defaultdict(int)
    file_counts = defaultdict(int)
    
    root_path = Path(root_dir)
    total_files = get_total_files(root_dir, include_extensions)
    
    print(f"\nFound {total_files:,} files to analyze")
    progress = ProgressLogger(total_files)
    
    for ext in include_extensions:
        if verbose:
            print(f"\nAnalyzing {ext} files...")
        
        pattern = f"**/*{ext}"
        for file_path in root_path.glob(pattern):
            # Check if file should be excluded
            if any(exclude in str(file_path) for exclude in exclude_dirs):
                continue
                
            if any(file_path.match(pattern) for pattern in exclude_files):
                continue
            
            if verbose:
                relative_path = file_path.relative_to(root_path)
                print(f"\nProcessing: {relative_path}")
            
            lines = count_lines(file_path)
            stats[ext] += lines
            file_counts[ext] += 1
            progress.update()
    
    duration = progress.finish()
    
    print(f"\nAnalysis completed in {duration:.2f} seconds")
    return stats, file_counts

def format_results(stats, file_counts):
    """Format the analysis results."""
    total_lines = sum(stats.values())
    total_files = sum(file_counts.values())
    
    results = ["\nLines of Code Analysis Results"]
    results.append("=" * 30)
    results.append(f"Total Lines: {total_lines:,}")
    results.append(f"Total Files: {total_files:,}\n")
    
    results.append("Breakdown by Language:")
    results.append("-" * 20)
    for ext, lines in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        files = file_counts[ext]
        percentage = (lines / total_lines) * 100 if total_lines > 0 else 0
        avg_lines = lines / files if files > 0 else 0
        results.append(f"{ext:8} {lines:8,} lines ({percentage:5.1f}%) in {files:5,} files (avg: {avg_lines:.1f} lines/file)")
    
    return "\n".join(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count lines of code in a repository")
    parser.add_argument("repo_path", help="Path to the repository root")
    parser.add_argument("--exclude-dirs", nargs="*", help="Directories to exclude")
    parser.add_argument("--exclude-files", nargs="*", help="File patterns to exclude")
    parser.add_argument("--include-extensions", nargs="*", help="File extensions to include")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed progress")
    
    args = parser.parse_args()
    
    stats, file_counts = analyze_repo(
        args.repo_path,
        exclude_dirs=args.exclude_dirs,
        exclude_files=args.exclude_files,
        include_extensions=args.include_extensions,
        verbose=args.verbose
    )
    
    print(format_results(stats, file_counts))