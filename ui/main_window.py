"""Main Window for Word Identity Changer.

Assembles the full desktop workflow: old identity configuration indicator,
session input, document selection, non-blocking batch execution, and reporting.
"""

from pathlib import Path
from typing import List, Optional
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QFileDialog,
    QMessageBox,
    QProgressBar,
    QStackedWidget,
    QFrame,
)

from config.settings_manager import SettingsManager
from core.models import (
    ConflictResolution,
    FileValidationResult,
    IdentityConfig,
    ProcessingResult,
    ReplacementMode,
)
from ui.components.config_dialog import ConfigDialog
from ui.components.conflict_dialog import ConflictDialog
from ui.components.file_list_widget import FileListWidget
from ui.components.preview_dialog import PreviewDialog
from ui.components.report_widget import ReportWidget
from ui.theme import MAIN_STYLESHEET, get_status_badge_style
from workers.batch_worker import BatchProcessWorker, ScanWorker


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Word Identity Changer — Pengganti Identitas Mahasiswa")
        self.setMinimumSize(920, 680)
        self.setStyleSheet(MAIN_STYLESHEET)

        self.settings_mgr = SettingsManager()
        self.scan_worker: Optional[ScanWorker] = None
        self.batch_worker: Optional[BatchProcessWorker] = None

        self._init_ui()
        self._load_active_config()

    def _init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # 1. Top Bar / Header Card
        header_card = QFrame()
        header_card.setProperty("class", "CardFrame")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(12, 10, 12, 10)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        lbl_app_title = QLabel("Word Identity Changer")
        lbl_app_title.setProperty("class", "HeaderTitle")
        lbl_app_sub = QLabel("Automasi Penggantian Nama & NIM Dokumen DOCX Tanpa Merusak File Asli")
        lbl_app_sub.setProperty("class", "SubText")
        title_layout.addWidget(lbl_app_title)
        title_layout.addWidget(lbl_app_sub)
        h_layout.addLayout(title_layout)

        h_layout.addStretch()

        # Config status indicator
        config_status_box = QHBoxLayout()
        config_status_box.setSpacing(10)
        self.lbl_config_status = QLabel("Acuan: Memuat...")
        self.lbl_config_status.setStyleSheet(get_status_badge_style("info"))
        config_status_box.addWidget(self.lbl_config_status)

        self.btn_open_config = QPushButton("⚙️ Atur Identitas Lama")
        self.btn_open_config.clicked.connect(self._open_config_dialog)
        config_status_box.addWidget(self.btn_open_config)

        h_layout.addLayout(config_status_box)
        main_layout.addWidget(header_card)

        # 2. Stacked View (Page 0: Input Form & File List, Page 1: Report View)
        self.stacked_widget = QStackedWidget()

        # Page 0: Main Workflow Form
        self.form_page = QWidget()
        form_layout = QVBoxLayout(self.form_page)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(14)

        # Section A: Session Inputs & Mode Selection
        session_card = QFrame()
        session_card.setProperty("class", "CardFrame")
        s_layout = QVBoxLayout(session_card)
        s_layout.setSpacing(12)

        s_title = QLabel("1. Tentukan Identitas Baru & Mode Penggantian")
        s_title.setProperty("class", "SectionTitle")
        s_layout.addWidget(s_title)

        # Radio button mode selector
        mode_box = QHBoxLayout()
        mode_box.setSpacing(20)
        self.mode_group = QButtonGroup(self)

        self.rb_both = QRadioButton("Nama dan NIM Sekaligus")
        self.rb_both.setChecked(True)
        self.mode_group.addButton(self.rb_both, 1)
        mode_box.addWidget(self.rb_both)

        self.rb_name_only = QRadioButton("Hanya Ganti Nama")
        self.mode_group.addButton(self.rb_name_only, 2)
        mode_box.addWidget(self.rb_name_only)

        self.rb_nim_only = QRadioButton("Hanya Ganti NIM")
        self.mode_group.addButton(self.rb_nim_only, 3)
        mode_box.addWidget(self.rb_nim_only)

        mode_box.addStretch()
        s_layout.addLayout(mode_box)

        self.rb_both.toggled.connect(self._on_mode_changed)
        self.rb_name_only.toggled.connect(self._on_mode_changed)
        self.rb_nim_only.toggled.connect(self._on_mode_changed)

        # Input fields (Name & NIM)
        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(16)

        # New Name
        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        lbl_new_name = QLabel("Nama Baru Pengganti:")
        lbl_new_name.setProperty("class", "FieldLabel")
        self.txt_new_name = QLineEdit()
        self.txt_new_name.setPlaceholderText("Masukkan Nama Mahasiswa Baru")
        name_col.addWidget(lbl_new_name)
        name_col.addWidget(self.txt_new_name)
        fields_layout.addLayout(name_col)

        # New NIM
        nim_col = QVBoxLayout()
        nim_col.setSpacing(4)
        lbl_new_nim = QLabel("NIM Baru Pengganti (Awalan 0 Terjaga):")
        lbl_new_nim.setProperty("class", "FieldLabel")
        self.txt_new_nim = QLineEdit()
        self.txt_new_nim.setPlaceholderText("Masukkan NIM Baru (Contoh: 0701234567)")
        nim_col.addWidget(lbl_new_nim)
        nim_col.addWidget(self.txt_new_nim)
        fields_layout.addLayout(nim_col)

        s_layout.addLayout(fields_layout)
        form_layout.addWidget(session_card)

        # Section B: Document Selection & Output Folder
        docs_card = QFrame()
        docs_card.setProperty("class", "CardFrame")
        d_layout = QVBoxLayout(docs_card)
        d_layout.setSpacing(12)

        d_title = QLabel("2. Pilih Dokumen Word (.docx) & Folder Keluaran")
        d_title.setProperty("class", "SectionTitle")
        d_layout.addWidget(d_title)

        # File List Widget
        self.file_list_widget = FileListWidget()
        d_layout.addWidget(self.file_list_widget)

        # Output Folder Selector
        out_layout = QHBoxLayout()
        out_layout.setSpacing(10)
        lbl_out = QLabel("Folder Keluaran Hasil:")
        lbl_out.setProperty("class", "FieldLabel")
        out_layout.addWidget(lbl_out)

        default_out = Path.home() / "Documents" / "WordIdentityChanger_Output"
        self.txt_output_dir = QLineEdit(str(default_out))
        out_layout.addWidget(self.txt_output_dir)

        self.btn_browse_out = QPushButton("Pilih Folder...")
        self.btn_browse_out.clicked.connect(self._browse_output_dir)
        out_layout.addWidget(self.btn_browse_out)

        d_layout.addLayout(out_layout)
        form_layout.addWidget(docs_card)

        # Section C: Execution & Progress Bar
        action_card = QFrame()
        action_card.setProperty("class", "CardFrame")
        a_layout = QVBoxLayout(action_card)
        a_layout.setSpacing(10)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.lbl_progress_status = QLabel("")
        self.lbl_progress_status.setProperty("class", "SubText")
        self.lbl_progress_status.setVisible(False)

        a_layout.addWidget(self.lbl_progress_status)
        a_layout.addWidget(self.progress_bar)

        # Action Buttons
        btn_action_layout = QHBoxLayout()
        btn_action_layout.setSpacing(12)

        self.btn_cancel = QPushButton("Batalkan Proses")
        self.btn_cancel.setProperty("class", "DangerButton")
        self.btn_cancel.setVisible(False)
        self.btn_cancel.clicked.connect(self._cancel_current_task)
        btn_action_layout.addWidget(self.btn_cancel)

        btn_action_layout.addStretch()

        self.btn_start = QPushButton("Periksa & Mulai Penggantian")
        self.btn_start.setProperty("class", "PrimaryButton")
        self.btn_start.clicked.connect(self._on_start_clicked)
        btn_action_layout.addWidget(self.btn_start)

        a_layout.addLayout(btn_action_layout)
        form_layout.addWidget(action_card)

        self.stacked_widget.addWidget(self.form_page)

        # Page 1: Report Widget
        self.report_widget = ReportWidget()
        self.report_widget.new_batch_requested.connect(self._reset_to_new_batch)
        self.stacked_widget.addWidget(self.report_widget)

        main_layout.addWidget(self.stacked_widget)

    def _load_active_config(self) -> None:
        """Loads and displays current old identity configuration."""
        name, nim = self.settings_mgr.load_config()
        if name and nim:
            self.lbl_config_status.setText(f"Acuan: {name} ({nim})")
            self.lbl_config_status.setStyleSheet(get_status_badge_style("success"))
        else:
            self.lbl_config_status.setText("Acuan: Belum Dikonfigurasi")
            self.lbl_config_status.setStyleSheet(get_status_badge_style("warning"))

    def _open_config_dialog(self) -> None:
        dialog = ConfigDialog(self, settings_mgr=self.settings_mgr)
        dialog.saved_signal.connect(lambda n, m: self._load_active_config())
        dialog.exec()

    def _on_mode_changed(self) -> None:
        """Enables/disables fields according to active replacement mode."""
        mode = self._get_current_mode()
        if mode == ReplacementMode.NAME_ONLY:
            self.txt_new_name.setEnabled(True)
            self.txt_new_nim.setEnabled(False)
        elif mode == ReplacementMode.NIM_ONLY:
            self.txt_new_name.setEnabled(False)
            self.txt_new_nim.setEnabled(True)
        else:
            self.txt_new_name.setEnabled(True)
            self.txt_new_nim.setEnabled(True)

    def _get_current_mode(self) -> ReplacementMode:
        if self.rb_name_only.isChecked():
            return ReplacementMode.NAME_ONLY
        elif self.rb_nim_only.isChecked():
            return ReplacementMode.NIM_ONLY
        return ReplacementMode.BOTH

    def _browse_output_dir(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Keluaran Hasil")
        if folder:
            self.txt_output_dir.setText(folder)

    def _on_start_clicked(self) -> None:
        """Validates inputs and starts pre-scan worker."""
        # 1. Validate old identity
        old_name, old_nim = self.settings_mgr.load_config()
        if not old_name or not old_nim:
            QMessageBox.warning(
                self,
                "Konfigurasi Belum Diisi",
                "Harap atur identitas lama (Nama dan NIM acuan) terlebih dahulu melalui tombol '⚙️ Atur Identitas Lama'.",
            )
            self._open_config_dialog()
            return

        old_id = IdentityConfig(name=old_name, nim=old_nim)

        # 2. Validate new identity
        mode = self._get_current_mode()
        new_name = self.txt_new_name.text().strip()
        new_nim = self.txt_new_nim.text().strip()
        new_id = IdentityConfig(name=new_name, nim=new_nim)

        valid, err = new_id.is_valid_for_mode(mode)
        if not valid:
            QMessageBox.warning(self, "Input Tidak Lengkap", err)
            return

        # Warning if new identity equals old identity
        if (mode in (ReplacementMode.NAME_ONLY, ReplacementMode.BOTH) and new_name == old_name) and (
            mode in (ReplacementMode.NIM_ONLY, ReplacementMode.BOTH) and new_nim == old_nim
        ):
            confirm = QMessageBox.question(
                self,
                "Identitas Sama",
                "Identitas baru sama dengan identitas lama. Tidak ada perubahan yang akan dilakukan. Lanjutkan?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if confirm != QMessageBox.Yes:
                return

        # 3. Validate file list
        files = self.file_list_widget.get_files()
        if not files:
            QMessageBox.warning(
                self, "Tidak Ada File", "Pilih minimal satu file .docx untuk diproses."
            )
            return

        # 4. Validate output directory
        out_dir = Path(self.txt_output_dir.text().strip())
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            QMessageBox.warning(
                self, "Folder Tidak Valid", f"Tidak dapat menggunakan folder keluaran: {str(e)}"
            )
            return

        # 5. Start background scan
        self._start_scan(files, old_id, new_id, mode, out_dir)

    def _start_scan(
        self,
        files: List[Path],
        old_id: IdentityConfig,
        new_id: IdentityConfig,
        mode: ReplacementMode,
        out_dir: Path,
    ) -> None:
        self.btn_start.setEnabled(False)
        self.btn_cancel.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(files))
        self.progress_bar.setValue(0)
        self.lbl_progress_status.setVisible(True)
        self.lbl_progress_status.setText("Memeriksa dan mencari kecocokan pada dokumen...")

        self.scan_worker = ScanWorker(files, old_id, mode)
        self.scan_worker.progress_signal.connect(self._on_scan_progress)
        self.scan_worker.finished_signal.connect(
            lambda res: self._on_scan_finished(res, files, old_id, new_id, mode, out_dir)
        )
        self.scan_worker.start()

    def _on_scan_progress(self, current: int, total: int, filename: str) -> None:
        self.progress_bar.setValue(current)
        self.lbl_progress_status.setText(f"Memeriksa {current}/{total}: {filename}")

    def _on_scan_finished(
        self,
        validation_results: List[FileValidationResult],
        files: List[Path],
        old_id: IdentityConfig,
        new_id: IdentityConfig,
        mode: ReplacementMode,
        out_dir: Path,
    ) -> None:
        self.progress_bar.setVisible(False)
        self.lbl_progress_status.setVisible(False)
        self.btn_cancel.setVisible(False)
        self.btn_start.setEnabled(True)

        # Show preview dialog
        preview = PreviewDialog(validation_results, self)
        if preview.exec() == PreviewDialog.Accepted:
            # User confirmed, start batch processing
            self._start_batch_processing(files, old_id, new_id, mode, out_dir)

    def _start_batch_processing(
        self,
        files: List[Path],
        old_id: IdentityConfig,
        new_id: IdentityConfig,
        mode: ReplacementMode,
        out_dir: Path,
    ) -> None:
        self.btn_start.setEnabled(False)
        self.btn_cancel.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(files))
        self.progress_bar.setValue(0)
        self.lbl_progress_status.setVisible(True)
        self.lbl_progress_status.setText("Memproses penggantian identitas...")

        self.batch_worker = BatchProcessWorker(
            files=files,
            output_dir=out_dir,
            old_identity=old_id,
            new_identity=new_id,
            mode=mode,
            conflict_resolution=ConflictResolution.AUTO_RENAME,
        )
        self.batch_worker.progress_signal.connect(self._on_batch_progress)
        self.batch_worker.finished_signal.connect(
            lambda res: self._on_batch_finished(res, out_dir)
        )
        self.batch_worker.start()

    def _on_batch_progress(self, current: int, total: int, filename: str) -> None:
        self.progress_bar.setValue(current)
        self.lbl_progress_status.setText(f"Memproses {current}/{total}: {filename}")

    def _on_batch_finished(self, results: List[ProcessingResult], out_dir: Path) -> None:
        self.progress_bar.setVisible(False)
        self.lbl_progress_status.setVisible(False)
        self.btn_cancel.setVisible(False)
        self.btn_start.setEnabled(True)

        # Switch to report page
        self.report_widget.set_results(out_dir, results)
        self.stacked_widget.setCurrentWidget(self.report_widget)

    def _cancel_current_task(self) -> None:
        if self.scan_worker and self.scan_worker.isRunning():
            self.scan_worker.cancel()
        if self.batch_worker and self.batch_worker.isRunning():
            self.batch_worker.cancel()

    def _reset_to_new_batch(self) -> None:
        self.file_list_widget.clear_files()
        self.stacked_widget.setCurrentWidget(self.form_page)
