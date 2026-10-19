"""Settings Manager for Word Identity Changer.

Handles persistent storage and retrieval of old identity (Name and NIM)
to a local JSON configuration file.
"""

import json
import os
from pathlib import Path
from typing import Optional, Tuple


def get_default_config_path() -> Path:
    """Returns the default configuration file path.
    
    Prefers user's AppData/WordIdentityChanger directory, fallback to current directory.
    """
    app_data = os.getenv("APPDATA")
    if app_data:
        config_dir = Path(app_data) / "WordIdentityChanger"
    else:
        config_dir = Path.home() / ".word_identity_changer"
    
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"
    except Exception:
        # Fallback to local directory
        return Path("config.json")


class SettingsManager:
    """Manages loading, saving, and validating application settings."""

    def __init__(self, config_file: Optional[Path] = None) -> None:
        self.config_file = config_file or get_default_config_path()

    @staticmethod
    def validate_identity(name: str, nim: str) -> Tuple[bool, Optional[str]]:
        """Validates that old name and old NIM are non-empty strings.
        
        NIM is strictly treated as a string to preserve leading zeroes.
        """
        clean_name = str(name).strip() if name is not None else ""
        clean_nim = str(nim).strip() if nim is not None else ""

        if not clean_name:
            return False, "Nama lama tidak boleh kosong."
        if not clean_nim:
            return False, "NIM lama tidak boleh kosong."
        return True, None

    def load_config(self) -> Tuple[str, str]:
        """Loads old_name and old_nim from JSON configuration.
        
        Returns:
            Tuple[str, str]: (old_name, old_nim). Returns ("", "") if file does not exist or is invalid.
        """
        if not self.config_file.exists():
            return "", ""

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            old_name = str(data.get("old_name", "")).strip()
            # Ensure NIM is strictly string to preserve leading zeroes
            old_nim = str(data.get("old_nim", "")).strip()
            return old_name, old_nim
        except (json.JSONDecodeError, OSError):
            # If file is corrupted or cannot be read, return empty strings gracefully
            return "", ""

    def save_config(self, name: str, nim: str) -> Tuple[bool, Optional[str]]:
        """Saves old_name and old_nim to the configuration file.
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        valid, err = self.validate_identity(name, nim)
        if not valid:
            return False, err

        clean_name = str(name).strip()
        clean_nim = str(nim).strip()

        data = {
            "old_name": clean_name,
            "old_nim": clean_nim
        }

        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True, None
        except OSError as e:
            return False, f"Gagal menyimpan konfigurasi: {str(e)}"
