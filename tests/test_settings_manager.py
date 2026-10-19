"""Unit tests for SettingsManager."""

import tempfile
import unittest
from pathlib import Path
from config.settings_manager import SettingsManager


class TestSettingsManager(unittest.TestCase):
    def test_settings_validation(self):
        # Empty cases
        valid, err = SettingsManager.validate_identity("", "12345")
        self.assertFalse(valid)
        self.assertIn("Nama lama tidak boleh kosong", err)

        valid, err = SettingsManager.validate_identity("Budi", "")
        self.assertFalse(valid)
        self.assertIn("NIM lama tidak boleh kosong", err)

        # Valid case
        valid, err = SettingsManager.validate_identity("Budi Santoso", "0701234567")
        self.assertTrue(valid)
        self.assertIsNone(err)

    def test_settings_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "test_config.json"
            manager = SettingsManager(config_file=config_file)

            # Initially empty
            name, nim = manager.load_config()
            self.assertEqual(name, "")
            self.assertEqual(nim, "")

            # Save with leading zero NIM
            success, err = manager.save_config("Ahmad Dahlan", "0123456789")
            self.assertTrue(success)
            self.assertIsNone(err)
            self.assertTrue(config_file.exists())

            # Load back
            loaded_name, loaded_nim = manager.load_config()
            self.assertEqual(loaded_name, "Ahmad Dahlan")
            self.assertEqual(loaded_nim, "0123456789")
            self.assertIsInstance(loaded_nim, str)
            self.assertTrue(loaded_nim.startswith("0"))

    def test_settings_corrupted_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_file = Path(tmp_dir) / "corrupted_config.json"
            config_file.write_text("{invalid json...", encoding="utf-8")

            manager = SettingsManager(config_file=config_file)
            name, nim = manager.load_config()
            self.assertEqual(name, "")
            self.assertEqual(nim, "")


if __name__ == "__main__":
    unittest.main()
