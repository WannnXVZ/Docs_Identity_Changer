"""Tests for UI components and business flow."""

import sys
import tempfile
import unittest
from pathlib import Path

# Only run if PySide6 is available
try:
    from PySide6.QtWidgets import QApplication
    from config.settings_manager import SettingsManager
    from core.models import ReplacementMode
    from ui.components.config_dialog import ConfigDialog
    from ui.components.file_list_widget import FileListWidget
    from ui.components.preview_dialog import PreviewDialog
    from ui.main_window import MainWindow
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


@unittest.skipUnless(PYSIDE6_AVAILABLE, "PySide6 not yet installed")
class TestUIComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure a single QApplication instance exists for GUI tests
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_file_list_widget(self):
        widget = FileListWidget()
        with tempfile.TemporaryDirectory() as tmp_dir:
            f1 = Path(tmp_dir) / "doc1.docx"
            f1.write_text("dummy", encoding="utf-8")
            f2 = Path(tmp_dir) / "doc2.docx"
            f2.write_text("dummy", encoding="utf-8")

            # Add files
            widget.add_files([f1, f2])
            self.assertEqual(len(widget.get_files()), 2)
            self.assertEqual(widget.table.rowCount(), 2)

            # Remove single file
            widget.remove_file(f1)
            self.assertEqual(len(widget.get_files()), 1)

            # Clear all
            widget.clear_files()
            self.assertEqual(len(widget.get_files()), 0)

    def test_main_window_initialization(self):
        window = MainWindow()
        self.assertIsNotNone(window)
        self.assertEqual(window.stacked_widget.currentIndex(), 0)

        # Mode switching toggles inputs
        window.rb_name_only.setChecked(True)
        self.assertTrue(window.txt_new_name.isEnabled())
        self.assertFalse(window.txt_new_nim.isEnabled())

        window.rb_nim_only.setChecked(True)
        self.assertFalse(window.txt_new_name.isEnabled())
        self.assertTrue(window.txt_new_nim.isEnabled())

        window.rb_both.setChecked(True)
        self.assertTrue(window.txt_new_name.isEnabled())
        self.assertTrue(window.txt_new_nim.isEnabled())


if __name__ == "__main__":
    unittest.main()
