import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import HTTPException

class StaticManager:
    """
    Utility class for managing static files and directories.
    
    Attributes:
        base_dir: Base directory for static files
        backup_dir: Directory for backups
    """
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.backup_dir = self.base_dir / "backups"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.base_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)

    def save_json(self, filename: str, data: Any) -> Path:
        """
        Save data as JSON file in the static directory.
        
        Args:
            filename: Name of the file (with or without .json extension)
            data: Data to save (must be JSON serializable)
            
        Returns:
            Path: Path to the saved file
            
        Raises:
            HTTPException: If file operation fails
        """
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        file_path = self.base_dir / filename
        try:
            with file_path.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return file_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    def load_json(self, filename: str) -> Any:
        """
        Load data from a JSON file.
        
        Args:
            filename: Name of the file (with or without .json extension)
            
        Returns:
            Any: Parsed JSON data
            
        Raises:
            HTTPException: If file doesn't exist or is invalid
        """
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
            
        file_path = self.base_dir / filename
        try:
            with file_path.open('r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File {filename} not found")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail=f"Invalid JSON in {filename}")

    def create_backup(self, filename: str) -> Path:
        """
        Create a backup of a file with timestamp.
        
        Args:
            filename: Name of the file to backup
            
        Returns:
            Path: Path to the backup file
            
        Raises:
            HTTPException: If backup operation fails
        """
        source_path = self.base_dir / filename
        if not source_path.exists():
            raise HTTPException(status_code=404, detail=f"File {filename} not found")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename.rsplit('.', 1)[0]}_{timestamp}.{filename.rsplit('.', 1)[1]}"
        backup_path = self.backup_dir / backup_filename

        try:
            shutil.copy2(source_path, backup_path)
            return backup_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")

    def list_files(self, extension: Optional[str] = None) -> List[str]:
        """
        List all files in the static directory.
        
        Args:
            extension: Optional file extension filter (e.g., 'json')
            
        Returns:
            List[str]: List of filenames
        """
        files = []
        for file in self.base_dir.iterdir():
            if file.is_file():
                if extension:
                    if file.suffix == f".{extension}":
                        files.append(file.name)
                else:
                    files.append(file.name)
        return files

    def list_backups(self, original_filename: Optional[str] = None) -> List[str]:
        """
        List all backups, optionally filtered by original filename.
        
        Args:
            original_filename: Optional original filename to filter backups
            
        Returns:
            List[str]: List of backup filenames
        """
        backups = []
        for file in self.backup_dir.iterdir():
            if file.is_file():
                if original_filename:
                    if file.name.startswith(original_filename.rsplit('.', 1)[0]):
                        backups.append(file.name)
                else:
                    backups.append(file.name)
        return backups

    def delete_file(self, filename: str, create_backup: bool = True) -> None:
        """
        Delete a file from the static directory.
        
        Args:
            filename: Name of the file to delete
            create_backup: Whether to create a backup before deletion
            
        Raises:
            HTTPException: If deletion fails
        """
        file_path = self.base_dir / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File {filename} not found")

        try:
            if create_backup:
                self.create_backup(filename)
            file_path.unlink()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

    def restore_backup(self, backup_filename: str) -> Path:
        """
        Restore a file from backup.
        
        Args:
            backup_filename: Name of the backup file to restore
            
        Returns:
            Path: Path to the restored file
            
        Raises:
            HTTPException: If restoration fails
        """
        backup_path = self.backup_dir / backup_filename
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail=f"Backup {backup_filename} not found")

        original_filename = backup_filename.split('_')[0] + '.' + backup_filename.rsplit('.', 1)[1]
        target_path = self.base_dir / original_filename

        try:
            if target_path.exists():
                self.create_backup(original_filename)
            shutil.copy2(backup_path, target_path)
            return target_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}") 