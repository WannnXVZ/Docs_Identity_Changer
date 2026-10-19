"""Data models and enums for Word Identity Changer."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class ReplacementMode(str, Enum):
    """Replacement mode options."""
    NAME_ONLY = "name_only"
    NIM_ONLY = "nim_only"
    BOTH = "both"

    @property
    def label(self) -> str:
        if self == ReplacementMode.NAME_ONLY:
            return "Nama Saja"
        elif self == ReplacementMode.NIM_ONLY:
            return "NIM Saja"
        return "Nama dan NIM"


class FileProcessStatus(str, Enum):
    """File processing and validation status."""
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    SUCCESS = "success"                   # Berhasil diproses
    NO_TARGET = "no_target"               # Tidak ditemukan identitas target
    NEEDS_REVIEW = "needs_review"         # Memerlukan pemeriksaan lebih lanjut
    FAILED = "failed"                     # Gagal diproses
    CANCELLED = "cancelled"               # Dibatalkan oleh pengguna

    @property
    def display_label(self) -> str:
        labels = {
            FileProcessStatus.PENDING: "Menunggu",
            FileProcessStatus.VALID: "Valid",
            FileProcessStatus.INVALID: "Tidak Valid",
            FileProcessStatus.SUCCESS: "Berhasil diproses",
            FileProcessStatus.NO_TARGET: "Tidak ditemukan identitas target",
            FileProcessStatus.NEEDS_REVIEW: "Memerlukan pemeriksaan lebih lanjut",
            FileProcessStatus.FAILED: "Gagal diproses",
            FileProcessStatus.CANCELLED: "Dibatalkan",
        }
        return labels.get(self, str(self.value))


class ConflictResolution(str, Enum):
    """Output filename conflict resolution."""
    AUTO_RENAME = "auto_rename"
    OVERWRITE = "overwrite"
    SKIP = "skip"


@dataclass
class IdentityConfig:
    """Identity data container (strictly string for NIM)."""
    name: str = ""
    nim: str = ""

    def __post_init__(self) -> None:
        self.name = str(self.name).strip() if self.name is not None else ""
        # String treatment preserves leading zeroes (e.g., '01234')
        self.nim = str(self.nim).strip() if self.nim is not None else ""

    def is_valid_for_mode(self, mode: ReplacementMode) -> tuple[bool, Optional[str]]:
        """Validates if identity fields are present for the selected mode."""
        if mode in (ReplacementMode.NAME_ONLY, ReplacementMode.BOTH):
            if not self.name:
                return False, "Nama baru wajib diisi untuk mode yang dipilih."
        if mode in (ReplacementMode.NIM_ONLY, ReplacementMode.BOTH):
            if not self.nim:
                return False, "NIM baru wajib diisi untuk mode yang dipilih."
        return True, None


@dataclass
class TargetMatchCount:
    """Number of occurrences found in a document."""
    name_matches: int = 0
    nim_matches: int = 0

    @property
    def total_matches(self) -> int:
        return self.name_matches + self.nim_matches


@dataclass
class FileValidationResult:
    """Result of pre-processing validation and target scanning."""
    file_path: Path
    is_valid: bool
    status: FileProcessStatus = FileProcessStatus.VALID
    error_message: Optional[str] = None
    match_count: TargetMatchCount = field(default_factory=TargetMatchCount)
    details: str = ""


@dataclass
class ProcessingResult:
    """Final result of replacement and verification per document."""
    source_file: Path
    output_file: Optional[Path] = None
    status: FileProcessStatus = FileProcessStatus.PENDING
    status_message: str = ""
    matches_replaced: TargetMatchCount = field(default_factory=TargetMatchCount)
    verified: bool = False
    warning: Optional[str] = None
