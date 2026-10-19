"""File List Widget with Multi-Select and Drag-and-Drop Support.

Displays selected .docx documents in a clean table with file sizes and removal actions.
"""

from pathlib import Path
from typing import List
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QLabel,
    QFileDialog,
    QMessageBox,
)


def format_file_size(size_bytes: int) -> str:
    """Formats bytes into human readable size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


class FileListWidget(QWidget):
    """Widget for managing the list of documents to process."""

    files_changed = Signal(list)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._files: List[Path] = []
        self.setAcceptDrops(True)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header controls
        ctrl_layout = QHBoxLayout()
        self.lbl_count = QLabel("0 dokumen dipilih")
        self.lbl_count.setProperty("class", "FieldLabel")
        ctrl_layout.addWidget(self.lbl_count)
        ctrl_layout.addStretch()

        self.btn_add = QPushButton(" Tambah File .docx")
        self.btn_add.clicked.connect(self._browse_files)
        ctrl_layout.addWidget(self.btn_add)

        self.btn_clear = QPushButton("Bersihkan Semua")
        self.btn_clear.clicked.connect(self.clear_files)
        ctrl_layout.addWidget(self.btn_clear)

        layout.addLayout(ctrl_layout)

        # Table Widget
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Nama File", "Ukuran", "Aksi"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        new_paths = []
        for url in urls:
            path = Path(url.toLocalFile())
            if path.is_file() and path.suffix.lower() == ".docx":
                new_paths.append(path)
            elif path.is_file():
                QMessageBox.warning(
                    self,
                    "Format Tidak Didukung",
                    f"File '{path.name}' bukan format .docx dan tidak dapat diproses.",
                )
        if new_paths:
            self.add_files(new_paths)

    def _browse_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Pilih Dokumen Word (.docx)",
            "",
            "Word Documents (*.docx)",
        )
        if files:
            paths = [Path(f) for f in files]
            self.add_files(paths)

    def add_files(self, paths: List[Path]) -> None:
        existing_set = {p.resolve() for p in self._files}
        added = False
        for p in paths:
            if p.suffix.lower() == ".docx" and p.resolve() not in existing_set:
                self._files.append(p)
                existing_set.add(p.resolve())
                added = True

        if added:
            self._refresh_table()
            self.files_changed.emit(self._files)

    def remove_file(self, path: Path) -> None:
        if path in self._files:
            self._files.remove(path)
            self._refresh_table()
            self.files_changed.emit(self._files)

    def clear_files(self) -> None:
        if not self._files:
            return
        self._files.clear()
        self._refresh_table()
        self.files_changed.emit(self._files)

    def get_files(self) -> List[Path]:
        return list(self._files)

    def _refresh_table(self) -> None:
        self.table.setRowCount(len(self._files))
        for row, path in enumerate(self._files):
            # Name item
            name_item = QTableWidgetItem(path.name)
            name_item.setToolTip(str(path))
            self.table.setItem(row, 0, name_item)

            # Size item
            size_str = format_file_size(path.stat().st_size) if path.exists() else "-"
            size_item = QTableWidgetItem(size_str)
            size_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, size_item)

            # Action button
            btn_del = QPushButton("Hapus")
            btn_del.setFixedWidth(64)
            btn_del.clicked.connect(lambda _, p=path: self.remove_file(p))
            self.table.setCellWidget(row, 2, btn_del)

        self.lbl_count.setText(f"{len(self._files)} dokumen dipilih")
