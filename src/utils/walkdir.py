import os
import json
from pathlib import Path
from typing import List, Dict

class CodeCollector:
    """
    Utility for walking directories and collecting Python source code files.
    
    Attributes:
        excluded_paths: List of path patterns to exclude
        output_file: Path to the output JSON file
    """
    
    def __init__(self, output_file: str = 'code_collection.json'):
        self.excluded_paths = [
            'node_modules', 'venv', '.env', '.git',
            'build', 'dist', '__pycache__', 
            '.pytest_cache', '.vscode', 'site-packages'
        ]
        self.output_file = output_file

    def is_path_excluded(self, path: str) -> bool:
        """
        Check if path should be excluded based on patterns.
        
        Args:
            path: Path to check
            
        Returns:
            bool: True if path should be excluded
        """
        return any(excluded in Path(path).parts for excluded in self.excluded_paths)

    def collect_python_files(self, root_dir: str) -> Dict[str, str]:
        """
        Walk through directory and collect Python files.
        
        Args:
            root_dir: Root directory to start walking from
            
        Returns:
            Dict[str, str]: Dictionary mapping file paths to their content
        """
        root_path = Path(root_dir).resolve()
        collected_files = {}
        
        for path in root_path.rglob('*.py'):
            try:
                # Convert to relative path for checking exclusions
                rel_path = path.relative_to(root_path)
                
                # Skip if path contains excluded patterns
                if self.is_path_excluded(str(rel_path)):
                    continue
                
                # Read file content
                content = path.read_text(encoding='utf-8')
                collected_files[str(rel_path)] = content
                
            except Exception as e:
                print(f"Error reading {path}: {e}")
                        
        return collected_files

    def save_collection(self, collection: Dict[str, str]) -> None:
        """
        Save collected files to JSON.
        
        Args:
            collection: Dictionary of collected files
        """
        try:
            # Ensure directory exists
            Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(collection, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving collection: {e}")

    def load_collection(self) -> Dict[str, str]:
        """
        Load previously collected files from JSON.
        
        Returns:
            Dict[str, str]: Dictionary of collected files
        """
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"No collection file found at {self.output_file}")
            return {}
        except Exception as e:
            print(f"Error loading collection: {e}")
            return {}

    def collect_and_save(self, root_dir: str) -> Dict[str, str]:
        """
        Collect Python files and save to JSON in one operation.
        
        Args:
            root_dir: Root directory to start walking from
            
        Returns:
            Dict[str, str]: Dictionary of collected files
        """
        collection = self.collect_python_files(root_dir)
        self.save_collection(collection)
        return collection

def main():
    """Main function to demonstrate usage."""
    collector = CodeCollector()
    
    # Use current directory as root
    root_dir = '.'
    
    print("Collecting Python files...")
    collection = collector.collect_and_save(root_dir)
    
    print("\nCollected files:")
    for path in collection.keys():
        print(f"- {path}")
    
    print(f"\nCollection saved to {collector.output_file}")

if __name__ == "__main__":
    main()