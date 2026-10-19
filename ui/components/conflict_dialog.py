"""Conflict Resolution Dialog for Existing Output Files.

Prompts user when an output file with the same name already exists in the destination.
"""

from typing import Tuple
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QCheckBox,
    QButtonGroup,
    QFrame,
)

from core.models import ConflictResolution
from ui.theme import MAIN_STYLESHEET


class ConflictDialog(QDialog):
    """Modal dialog to resolve filename collision."""

    def __init__(self, filename: str, destination_dir: str, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.destination_dir = destination_dir
        self.setWindowTitle("Konflik Nama File Keluaran")
        self.setFixedWidth(460)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.setModal(True)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        card = QFrame()
        card.setProperty("class", "CardFrame")
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(8)

        title = QLabel("File Sudah Ada di Folder Keluaran")
        title.setProperty("class", "HeaderTitle")
        c_layout.addWidget(title)

        desc = QLabel(
            f"File <b>{self.filename}</b> sudah ada di folder tujuan:<br>"
            f"<code>{self.destination_dir}</code><br><br>"
            "Pilih tindakan yang ingin Anda lakukan:"
        )
        desc.setWordWrap(True)
        c_layout.addWidget(desc)

        layout.addWidget(card)

        # Options frame
        opts_frame = QFrame()
        opts_frame.setProperty("class", "SectionFrame")
        opt_layout = QVBoxLayout(opts_frame)
        opt_layout.setSpacing(10)

        self.btn_group = QButtonGroup(self)

        self.rb_rename = QRadioButton("Ganti Nama Otomatis (Disarankan, contoh: _rev1.docx)")
        self.rb_rename.setChecked(True)
        self.btn_group.addButton(self.rb_rename, 1)
        opt_layout.addWidget(self.rb_rename)

        self.rb_overwrite = QRadioButton("Timpa File yang Sudah Ada")
        self.btn_group.addButton(self.rb_overwrite, 2)
        opt_layout.addWidget(self.rb_overwrite)

        self.rb_skip = QRadioButton("Lewati File Ini (Jangan Proses)")
        self.btn_group.addButton(self.rb_skip, 3)
        opt_layout.addWidget(self.rb_skip)

        layout.addWidget(opts_frame)

        # Apply to all checkbox
        self.chk_apply_all = QCheckBox("Terapkan keputusan ini untuk semua konflik berikutnya")
        layout.addWidget(self.chk_apply_all)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_ok = QPushButton("Lanjutkan")
        self.btn_ok.setProperty("class", "PrimaryButton")
        self.btn_ok.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_ok)

        layout.addLayout(btn_layout)

    def get_resolution(self) -> Tuple[ConflictResolution, bool]:
        """Returns selected resolution and whether to apply to all subsequent conflicts."""
        apply_all = self.chk_apply_all.isChecked()
        if self.rb_rename.isChecked():
            return ConflictResolution.AUTO_RENAME, apply_all
        elif self.rb_overwrite.isChecked():
            return ConflictResolution.OVERWRITE, apply_all
        return ConflictResolution.SKIP, apply_all
