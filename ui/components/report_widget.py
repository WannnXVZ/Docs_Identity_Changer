"""Final Processing Report Widget.

Displays execution summary, per-file final status, and provides an action
to directly open the output directory in Windows File Explorer.
"""

import os
from pathlib import Path
from typing import List
from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
)

from core.models import FileProcessStatus, ProcessingResult
from ui.theme import get_status_badge_style


class ReportWidget(QWidget):
    """Widget displaying final batch report."""

    new_batch_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.output_dir: Path = Path(".")
        self.results: List[ProcessingResult] = []
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header summary card
        card = QFrame()
        card.setProperty("class", "CardFrame")
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(8)

        title = QLabel("Laporan Akhir Pemrosesan Batch")
        title.setProperty("class", "HeaderTitle")
        c_layout.addWidget(title)

        self.lbl_summary = QLabel("Menampilkan status setiap file yang telah diproses.")
        self.lbl_summary.setProperty("class", "SubText")
        c_layout.addWidget(self.lbl_summary)

        # Stat pills
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(10)
        c_layout.addLayout(self.stats_layout)

        layout.addWidget(card)

        # Table
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Nama File", "Status Akhir", "Diganti", "Lokasi Hasil"]
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_open_folder = QPushButton("📁 Buka Folder Keluaran")
        self.btn_open_folder.setProperty("class", "PrimaryButton")
        self.btn_open_folder.clicked.connect(self._open_output_folder)
        btn_layout.addWidget(self.btn_open_folder)

        btn_layout.addStretch()

        self.btn_new_batch = QPushButton("Proses Batch Baru")
        self.btn_new_batch.clicked.connect(self.new_batch_requested.emit)
        btn_layout.addWidget(self.btn_new_batch)

        layout.addLayout(btn_layout)

    def set_results(self, output_dir: Path, results: List[ProcessingResult]) -> None:
        self.output_dir = output_dir
        self.results = results

        total = len(results)
        success_cnt = sum(1 for r in results if r.status == FileProcessStatus.SUCCESS)
        no_target_cnt = sum(1 for r in results if r.status == FileProcessStatus.NO_TARGET)
        review_cnt = sum(1 for r in results if r.status == FileProcessStatus.NEEDS_REVIEW)
        failed_cnt = sum(1 for r in results if r.status == FileProcessStatus.FAILED)

        # Clear and update stats layout
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        def add_stat_badge(text: str, badge_type: str) -> None:
            lbl = QLabel(text)
            lbl.setStyleSheet(get_status_badge_style(badge_type))
            self.stats_layout.addWidget(lbl)

        add_stat_badge(f"✓ {success_cnt} Berhasil", "success")
        if review_cnt > 0:
            add_stat_badge(f"⚠ {review_cnt} Perlu Pemeriksaan", "warning")
        if no_target_cnt > 0:
            add_stat_badge(f"ℹ {no_target_cnt} Tanpa Target", "info")
        if failed_cnt > 0:
            add_stat_badge(f"✕ {failed_cnt} Gagal", "danger")
        self.stats_layout.addStretch()

        self.lbl_summary.setText(
            f"Selesai memproses {total} dokumen. "
            f"File hasil disimpan di: {self.output_dir}"
        )

        # Populate table
        self.table.setRowCount(total)
        for row, res in enumerate(results):
            # Filename
            f_item = QTableWidgetItem(res.source_file.name)
            self.table.setItem(row, 0, f_item)

            # Status pill
            status_lbl = QLabel()
            if res.status == FileProcessStatus.SUCCESS:
                status_lbl.setText("Berhasil")
                status_lbl.setStyleSheet(get_status_badge_style("success"))
            elif res.status == FileProcessStatus.NEEDS_REVIEW:
                status_lbl.setText("Perlu Pemeriksaan")
                status_lbl.setStyleSheet(get_status_badge_style("warning"))
            elif res.status == FileProcessStatus.NO_TARGET:
                status_lbl.setText("Tanpa Target")
                status_lbl.setStyleSheet(get_status_badge_style("info"))
            else:
                status_lbl.setText("Gagal")
                status_lbl.setStyleSheet(get_status_badge_style("danger"))
            status_lbl.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 1, status_lbl)

            # Replaced count
            m_item = QTableWidgetItem(f"{res.matches_replaced.total_matches} target")
            m_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, m_item)

            # Output path
            path_str = str(res.output_file) if res.output_file else res.status_message
            out_item = QTableWidgetItem(path_str)
            self.table.setItem(row, 3, out_item)

    def _open_output_folder(self) -> None:
        if self.output_dir.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.output_dir)))
