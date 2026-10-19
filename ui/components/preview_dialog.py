"""Preview and Confirmation Dialog.

Displays scan results, match counts, and structural status for each document
before the user explicitly confirms batch execution.
"""

from typing import List
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
)

from core.models import FileProcessStatus, FileValidationResult
from ui.theme import MAIN_STYLESHEET, get_status_badge_style


class PreviewDialog(QDialog):
    """Dialog showing pre-execution scan results and user confirmation."""

    def __init__(self, validation_results: List[FileValidationResult], parent=None):
        super().__init__(parent)
        self.validation_results = validation_results
        self.setWindowTitle("Pratinjau Hasil Validasi Dokumen")
        self.resize(720, 480)
        self.setStyleSheet(MAIN_STYLESHEET)
        self.setModal(True)

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header card
        header_card = QFrame()
        header_card.setProperty("class", "CardFrame")
        h_layout = QVBoxLayout(header_card)
        h_layout.setSpacing(6)

        title = QLabel("Ringkasan Pemeriksaan Dokumen Sebelum Penggantian")
        title.setProperty("class", "HeaderTitle")
        h_layout.addWidget(title)

        sub = QLabel(
            "Periksa jumlah kecocokan identitas lama pada masing-masing dokumen. "
            "Dokumen sumber tidak akan diubah; hasil selalu disimpan sebagai file baru."
        )
        sub.setWordWrap(True)
        sub.setProperty("class", "SubText")
        h_layout.addWidget(sub)

        # Stats summary row
        total_files = len(self.validation_results)
        ready_files = sum(
            1 for r in self.validation_results if r.is_valid and r.status == FileProcessStatus.VALID
        )
        no_target_files = sum(
            1 for r in self.validation_results if r.status == FileProcessStatus.NO_TARGET
        )
        failed_files = sum(1 for r in self.validation_results if not r.is_valid)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        def make_stat_box(title_text: str, val_text: str, style_type: str) -> QFrame:
            box = QFrame()
            box.setProperty("class", "SectionFrame")
            blayout = QVBoxLayout(box)
            blayout.setContentsMargins(8, 6, 8, 6)
            blayout.setSpacing(2)
            lbl_t = QLabel(title_text)
            lbl_t.setProperty("class", "FieldLabel")
            lbl_v = QLabel(val_text)
            lbl_v.setStyleSheet(get_status_badge_style(style_type))
            blayout.addWidget(lbl_t)
            blayout.addWidget(lbl_v)
            return box

        stats_layout.addWidget(make_stat_box("Total Dokumen", f"{total_files} File", "info"))
        stats_layout.addWidget(make_stat_box("Siap Diproses", f"{ready_files} File", "success"))
        stats_layout.addWidget(
            make_stat_box("Tanpa Target", f"{no_target_files} File", "warning")
        )
        stats_layout.addWidget(make_stat_box("Gagal / Rusak", f"{failed_files} File", "danger"))
        h_layout.addLayout(stats_layout)

        layout.addWidget(header_card)

        # Table of preview
        self.table = QTableWidget(len(self.validation_results), 4)
        self.table.setHorizontalHeaderLabels(
            ["Nama File", "Status", "Kecocokan", "Keterangan"]
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        for row, res in enumerate(self.validation_results):
            # Filename
            f_item = QTableWidgetItem(res.file_path.name)
            self.table.setItem(row, 0, f_item)

            # Status pill
            status_widget = QLabel()
            if not res.is_valid:
                status_widget.setText("Gagal")
                status_widget.setStyleSheet(get_status_badge_style("danger"))
            elif res.status == FileProcessStatus.NO_TARGET:
                status_widget.setText("Tanpa Target")
                status_widget.setStyleSheet(get_status_badge_style("warning"))
            else:
                status_widget.setText("Valid")
                status_widget.setStyleSheet(get_status_badge_style("success"))
            status_widget.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 1, status_widget)

            # Matches
            total_m = res.match_count.total_matches
            m_item = QTableWidgetItem(f"{total_m} target" if res.is_valid else "-")
            m_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, m_item)

            # Details
            detail_str = res.error_message if not res.is_valid else res.details
            d_item = QTableWidgetItem(detail_str)
            self.table.setItem(row, 3, d_item)

        layout.addWidget(self.table)

        # Actions
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Batal")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_confirm = QPushButton("Konfirmasi & Mulai Penggantian")
        self.btn_confirm.setProperty("class", "PrimaryButton")
        self.btn_confirm.setEnabled(ready_files > 0)
        self.btn_confirm.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_confirm)

        layout.addLayout(btn_layout)
