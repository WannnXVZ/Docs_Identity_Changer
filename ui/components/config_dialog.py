"""Configuration Dialog for Old Identity Settings.

Allows user to view and update the persistent Old Name and Old NIM.
"""

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFrame,
)

from config.settings_manager import SettingsManager
from ui.theme import MAIN_STYLESHEET


class ConfigDialog(QDialog):
    """Modal dialog to configure old identity (Name and NIM)."""

    saved_signal = Signal(str, str)

    def __init__(self, parent: Optional[QDialog] = None, settings_mgr: Optional[SettingsManager] = None):
        super().__init__(parent)
        self.settings_mgr = settings_mgr or SettingsManager()
        self.setWindowTitle("Pengaturan Identitas Lama (Acuan)")
        self.setFixedWidth(460)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.setModal(True)

        self._init_ui()
        self._load_current_values()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header card
        card = QFrame()
        card.setProperty("class", "CardFrame")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)

        title = QLabel("Konfigurasi Identitas Lama")
        title.setProperty("class", "HeaderTitle")
        card_layout.addWidget(title)

        desc = QLabel(
            "Identitas ini disimpan secara permanen di aplikasi dan digunakan "
            "sebagai acuan pencarian teks target pada seluruh dokumen .docx."
        )
        desc.setWordWrap(True)
        desc.setProperty("class", "SubText")
        card_layout.addWidget(desc)

        layout.addWidget(card)

        # Form fields
        form_frame = QFrame()
        form_frame.setProperty("class", "SectionFrame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(12)

        # Nama Lama
        lbl_name = QLabel("Nama Mahasiswa Lama (Target Acuan):")
        lbl_name.setProperty("class", "FieldLabel")
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Contoh: Budi Santoso")
        form_layout.addWidget(lbl_name)
        form_layout.addWidget(self.txt_name)

        # NIM Lama
        lbl_nim = QLabel("NIM Lama (Target Acuan):")
        lbl_nim.setProperty("class", "FieldLabel")
        self.txt_nim = QLineEdit()
        self.txt_nim.setPlaceholderText("Contoh: 0701234567")
        form_layout.addWidget(lbl_nim)
        form_layout.addWidget(self.txt_nim)

        layout.addWidget(form_frame)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Batal")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Simpan Konfigurasi")
        self.btn_save.setProperty("class", "PrimaryButton")
        self.btn_save.clicked.connect(self._save_config)
        btn_layout.addWidget(self.btn_save)

        layout.addLayout(btn_layout)

    def _load_current_values(self) -> None:
        name, nim = self.settings_mgr.load_config()
        self.txt_name.setText(name)
        self.txt_nim.setText(nim)

    def _save_config(self) -> None:
        name = self.txt_name.text().strip()
        nim = self.txt_nim.text().strip()

        valid, err = self.settings_mgr.save_config(name, nim)
        if not valid:
            QMessageBox.warning(self, "Validasi Gagal", err or "Identitas tidak valid.")
            return

        self.saved_signal.emit(name, nim)
        QMessageBox.information(
            self,
            "Berhasil Disimpan",
            "Konfigurasi identitas lama berhasil diperbarui.",
        )
        self.accept()
