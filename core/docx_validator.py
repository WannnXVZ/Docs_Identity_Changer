"""DOCX Validator and Target Match Scanner.

Inspects .docx files for validity, structural integrity, and counts occurrences
of target identities in body paragraphs, tables, and headers/footers without
modifying the source file.
"""

from pathlib import Path
from typing import Optional, Set
from zipfile import BadZipFile
import docx
from docx.opc.exceptions import PackageNotFoundError
from docx.text.paragraph import Paragraph

from core.models import (
    FileProcessStatus,
    FileValidationResult,
    ReplacementMode,
    TargetMatchCount,
)
from core.run_replacer import count_matches_in_paragraph


def scan_paragraphs_for_matches(
    paragraphs: list[Paragraph], old_name: str, old_nim: str
) -> tuple[int, int]:
    """Scans a list of paragraphs for name and NIM matches."""
    name_count = 0
    nim_count = 0
    for p in paragraphs:
        if old_name:
            name_count += count_matches_in_paragraph(p, old_name)
        if old_nim:
            nim_count += count_matches_in_paragraph(p, old_nim)
    return name_count, nim_count


def scan_document_for_matches(
    doc: docx.Document, old_name: str, old_nim: str
) -> TargetMatchCount:
    """Scans all body paragraphs, tables, and headers/footers in the document."""
    total_name = 0
    total_nim = 0

    # 1. Scan body paragraphs
    n, m = scan_paragraphs_for_matches(doc.paragraphs, old_name, old_nim)
    total_name += n
    total_nim += m

    # 2. Scan all tables (and cells)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                n, m = scan_paragraphs_for_matches(cell.paragraphs, old_name, old_nim)
                total_name += n
                total_nim += m

    # 3. Scan headers and footers for each section
    seen_parts: Set[int] = set()
    for section in doc.sections:
        for hf_part in (
            section.header,
            section.footer,
            section.first_page_header,
            section.first_page_footer,
            section.even_page_header,
            section.even_page_footer,
        ):
            if hf_part is None:
                continue
            # Avoid duplicate counting if linked to previous section
            part_id = id(hf_part._element)
            if part_id in seen_parts:
                continue
            seen_parts.add(part_id)

            n, m = scan_paragraphs_for_matches(hf_part.paragraphs, old_name, old_nim)
            total_name += n
            total_nim += m

            for table in hf_part.tables:
                for row in table.rows:
                    for cell in row.cells:
                        n, m = scan_paragraphs_for_matches(
                            cell.paragraphs, old_name, old_nim
                        )
                        total_name += n
                        total_nim += m

    return TargetMatchCount(name_matches=total_name, nim_matches=total_nim)


class DocxValidator:
    """Validates files and scans for target identity occurrences."""

    @staticmethod
    def validate_and_scan(
        file_path: Path,
        old_name: str = "",
        old_nim: str = "",
        mode: ReplacementMode = ReplacementMode.BOTH,
    ) -> FileValidationResult:
        """Validates a single file and scans target matches.
        
        Guarantees source file immutability: opened in read mode only.
        """
        path = Path(file_path)

        # 1. Check file existence
        if not path.exists():
            return FileValidationResult(
                file_path=path,
                is_valid=False,
                status=FileProcessStatus.FAILED,
                error_message=f"File {path.name} tidak ditemukan.",
            )

        # 2. Check file format (.docx only)
        if path.suffix.lower() != ".docx":
            return FileValidationResult(
                file_path=path,
                is_valid=False,
                status=FileProcessStatus.INVALID,
                error_message=f"File {path.name} bukan format .docx dan tidak dapat diproses.",
            )

        # 3. Try opening and parsing document
        try:
            doc = docx.Document(path)
        except (PackageNotFoundError, BadZipFile, OSError):
            return FileValidationResult(
                file_path=path,
                is_valid=False,
                status=FileProcessStatus.FAILED,
                error_message=f"File {path.name} tidak dapat dibaca atau rusak.",
            )
        except Exception as e:
            return FileValidationResult(
                file_path=path,
                is_valid=False,
                status=FileProcessStatus.FAILED,
                error_message=f"File {path.name} tidak dapat dibaca atau rusak: {str(e)}",
            )

        # 4. Scan matches
        # Filter what to search based on mode
        search_name = old_name if mode in (ReplacementMode.NAME_ONLY, ReplacementMode.BOTH) else ""
        search_nim = old_nim if mode in (ReplacementMode.NIM_ONLY, ReplacementMode.BOTH) else ""

        match_counts = scan_document_for_matches(doc, search_name, search_nim)

        relevant_matches = 0
        if mode == ReplacementMode.NAME_ONLY:
            relevant_matches = match_counts.name_matches
        elif mode == ReplacementMode.NIM_ONLY:
            relevant_matches = match_counts.nim_matches
        else:
            relevant_matches = match_counts.total_matches

        if relevant_matches == 0:
            return FileValidationResult(
                file_path=path,
                is_valid=True,
                status=FileProcessStatus.NO_TARGET,
                match_count=match_counts,
                details=f"Identitas lama tidak ditemukan pada file {path.name}.",
            )

        detail_parts = []
        if search_name and match_counts.name_matches > 0:
            detail_parts.append(f"{match_counts.name_matches} Nama")
        if search_nim and match_counts.nim_matches > 0:
            detail_parts.append(f"{match_counts.nim_matches} NIM")

        summary_detail = f"Ditemukan {', '.join(detail_parts)}"
        if relevant_matches > 2:
            summary_detail += " (Kecocokan ganda terdeteksi)"

        return FileValidationResult(
            file_path=path,
            is_valid=True,
            status=FileProcessStatus.VALID,
            match_count=match_counts,
            details=summary_detail,
        )
