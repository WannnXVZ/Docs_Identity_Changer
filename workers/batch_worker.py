"""Background Workers for Non-Blocking Validation and Batch Document Processing.

Uses PySide6 QThread to ensure the UI remains fluid and responsive during IO operations,
providing progress notifications and cancellation support (FR-012, FR-017).
"""

from pathlib import Path
from typing import List, Optional
from PySide6.QtCore import QThread, Signal

from core.docx_engine import DocxEngine
from core.docx_validator import DocxValidator
from core.models import (
    ConflictResolution,
    FileProcessStatus,
    FileValidationResult,
    IdentityConfig,
    ProcessingResult,
    ReplacementMode,
)


class ScanWorker(QThread):
    """Background worker for scanning and validating documents before execution."""

    progress_signal = Signal(int, int, str)  # current, total, filename
    finished_signal = Signal(list)           # List[FileValidationResult]

    def __init__(
        self,
        files: List[Path],
        old_identity: IdentityConfig,
        mode: ReplacementMode = ReplacementMode.BOTH,
    ):
        super().__init__()
        self.files = files
        self.old_identity = old_identity
        self.mode = mode
        self._is_cancelled = False

    def cancel(self) -> None:
        self._is_cancelled = True

    def run(self) -> None:
        results: List[FileValidationResult] = []
        total = len(self.files)

        for idx, file_path in enumerate(self.files, start=1):
            if self._is_cancelled:
                break

            self.progress_signal.emit(idx, total, file_path.name)
            res = DocxValidator.validate_and_scan(
                file_path=file_path,
                old_name=self.old_identity.name,
                old_nim=self.old_identity.nim,
                mode=self.mode,
            )
            results.append(res)

        self.finished_signal.emit(results)


class BatchProcessWorker(QThread):
    """Background worker for batch replacement across multiple documents."""

    progress_signal = Signal(int, int, str)       # current, total, filename
    file_done_signal = Signal(ProcessingResult)    # single result
    finished_signal = Signal(list)                # List[ProcessingResult]

    def __init__(
        self,
        files: List[Path],
        output_dir: Path,
        old_identity: IdentityConfig,
        new_identity: IdentityConfig,
        mode: ReplacementMode = ReplacementMode.BOTH,
        conflict_resolution: ConflictResolution = ConflictResolution.AUTO_RENAME,
    ):
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        self.old_identity = old_identity
        self.new_identity = new_identity
        self.mode = mode
        self.conflict_resolution = conflict_resolution
        self._is_cancelled = False

    def cancel(self) -> None:
        """Requests cooperative cancellation of remaining files (FR-017)."""
        self._is_cancelled = True

    def run(self) -> None:
        results: List[ProcessingResult] = []
        total = len(self.files)

        for idx, file_path in enumerate(self.files, start=1):
            if self._is_cancelled:
                # Mark remaining files as cancelled
                for remaining in self.files[idx - 1 :]:
                    res = ProcessingResult(
                        source_file=remaining,
                        status=FileProcessStatus.CANCELLED,
                        status_message="Dibatalkan oleh pengguna.",
                    )
                    results.append(res)
                    self.file_done_signal.emit(res)
                break

            self.progress_signal.emit(idx, total, file_path.name)

            # Process single file with failure isolation (FR-012)
            try:
                res = DocxEngine.process_file(
                    source_file=file_path,
                    output_dir=self.output_dir,
                    old_identity=self.old_identity,
                    new_identity=self.new_identity,
                    mode=self.mode,
                    conflict_resolution=self.conflict_resolution,
                )
            except Exception as e:
                res = ProcessingResult(
                    source_file=file_path,
                    status=FileProcessStatus.FAILED,
                    status_message=f"Terjadi kesalahan teknis: {str(e)}",
                )

            results.append(res)
            self.file_done_signal.emit(res)

        self.finished_signal.emit(results)
