"""Integration tests for DocxValidator and DocxEngine across all PRD scenarios."""

import hashlib
import tempfile
import unittest
from pathlib import Path
import docx

from core.docx_engine import DocxEngine
from core.docx_validator import DocxValidator
from core.models import (
    ConflictResolution,
    FileProcessStatus,
    IdentityConfig,
    ReplacementMode,
)
from tests.create_test_docs import generate_all_test_documents


def get_file_hash(path: Path) -> str:
    """Calculates SHA256 hash of a file."""
    hasher = hashlib.sha256()
    hasher.update(path.read_bytes())
    return hasher.hexdigest()


class TestDocxEngineIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.sample_dir = Path(cls.temp_dir.name) / "samples"
        cls.docs = generate_all_test_documents(cls.sample_dir)

        cls.old_id = IdentityConfig(name="Budi Santoso", nim="0701234567")
        cls.new_id = IdentityConfig(name="Dewi Sartika", nim="0809876543")

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_validation_normal_file(self):
        """Tests validation on normal file with matches."""
        res = DocxValidator.validate_and_scan(
            self.docs["doc1"],
            old_name=self.old_id.name,
            old_nim=self.old_id.nim,
            mode=ReplacementMode.BOTH,
        )
        self.assertTrue(res.is_valid)
        self.assertEqual(res.status, FileProcessStatus.VALID)
        self.assertEqual(res.match_count.name_matches, 1)
        self.assertEqual(res.match_count.nim_matches, 1)

    def test_validation_corrupted_file(self):
        """Tests validation flags corrupted files without crashing (AC-012, FR-016)."""
        res = DocxValidator.validate_and_scan(
            self.docs["doc9"],
            old_name=self.old_id.name,
            old_nim=self.old_id.nim,
            mode=ReplacementMode.BOTH,
        )
        self.assertFalse(res.is_valid)
        self.assertEqual(res.status, FileProcessStatus.FAILED)
        self.assertIn("rusak", res.error_message.lower())

    def test_validation_no_target_file(self):
        """Tests validation detects document without target identity (AC-008, BR-006)."""
        res = DocxValidator.validate_and_scan(
            self.docs["doc7"],
            old_name=self.old_id.name,
            old_nim=self.old_id.nim,
            mode=ReplacementMode.BOTH,
        )
        self.assertTrue(res.is_valid)
        self.assertEqual(res.status, FileProcessStatus.NO_TARGET)

    def test_engine_simple_paragraph_replacement(self):
        """Tests replacement on simple paragraph (AC-004, AC-009, AC-011)."""
        with tempfile.TemporaryDirectory() as out_temp:
            out_dir = Path(out_temp)
            src = self.docs["doc1"]
            initial_hash = get_file_hash(src)

            result = DocxEngine.process_file(
                source_file=src,
                output_dir=out_dir,
                old_identity=self.old_id,
                new_identity=self.new_id,
                mode=ReplacementMode.BOTH,
            )

            # Check status
            self.assertEqual(result.status, FileProcessStatus.SUCCESS)
            self.assertTrue(result.verified)
            self.assertTrue(result.output_file.exists())

            # Source file MUST NOT be altered (BR-005, AC-009)
            self.assertEqual(get_file_hash(src), initial_hash)

            # Output file content verification
            doc = docx.Document(result.output_file)
            full_text = "\n".join(p.text for p in doc.paragraphs)
            self.assertIn("Dewi Sartika", full_text)
            self.assertIn("0809876543", full_text)
            self.assertNotIn("Budi Santoso", full_text)
            self.assertNotIn("0701234567", full_text)

    def test_engine_split_runs_replacement(self):
        """Tests replacement across split runs with styles preserved (Risiko N)."""
        with tempfile.TemporaryDirectory() as out_temp:
            out_dir = Path(out_temp)
            src = self.docs["doc2"]

            result = DocxEngine.process_file(
                source_file=src,
                output_dir=out_dir,
                old_identity=self.old_id,
                new_identity=self.new_id,
                mode=ReplacementMode.BOTH,
            )

            self.assertEqual(result.status, FileProcessStatus.SUCCESS)
            self.assertTrue(result.verified)

            doc = docx.Document(result.output_file)
            full_text = "\n".join(p.text for p in doc.paragraphs)
            self.assertIn("Dewi Sartika", full_text)
            self.assertIn("0809876543", full_text)

    def test_engine_table_replacement(self):
        """Tests replacement inside tables (Skenario 3 PRD)."""
        with tempfile.TemporaryDirectory() as out_temp:
            out_dir = Path(out_temp)
            src = self.docs["doc3"]

            result = DocxEngine.process_file(
                source_file=src,
                output_dir=out_dir,
                old_identity=self.old_id,
                new_identity=self.new_id,
                mode=ReplacementMode.BOTH,
            )

            self.assertEqual(result.status, FileProcessStatus.SUCCESS)
            doc = docx.Document(result.output_file)
            table_text = "\n".join(
                cell.text for row in doc.tables[0].rows for cell in row.cells
            )
            self.assertIn("Dewi Sartika", table_text)
            self.assertIn("0809876543", table_text)

    def test_engine_header_footer_replacement(self):
        """Tests replacement inside headers and footers (Skenario 4 PRD)."""
        with tempfile.TemporaryDirectory() as out_temp:
            out_dir = Path(out_temp)
            src = self.docs["doc4"]

            result = DocxEngine.process_file(
                source_file=src,
                output_dir=out_dir,
                old_identity=self.old_id,
                new_identity=self.new_id,
                mode=ReplacementMode.BOTH,
            )

            self.assertEqual(result.status, FileProcessStatus.SUCCESS)
            doc = docx.Document(result.output_file)
            section = doc.sections[0]
            header_text = section.header.paragraphs[0].text
            footer_text = section.footer.paragraphs[0].text

            self.assertIn("Dewi Sartika", header_text)
            self.assertIn("0809876543", header_text)
            self.assertIn("Dewi Sartika", footer_text)
            self.assertNotIn("Budi Santoso", header_text)

    def test_engine_substring_safety(self):
        """Tests that substring matches are prevented (BR-009, Skenario 6)."""
        with tempfile.TemporaryDirectory() as out_temp:
            out_dir = Path(out_temp)
            src = self.docs["doc6"]

            sub_old = IdentityConfig(name="Budi Santoso", nim="12345")
            sub_new = IdentityConfig(name="Dewi Sartika", nim="99999")

            result = DocxEngine.process_file(
                source_file=src,
                output_dir=out_dir,
                old_identity=sub_old,
                new_identity=sub_new,
                mode=ReplacementMode.BOTH,
            )

            self.assertEqual(result.status, FileProcessStatus.SUCCESS)
            doc = docx.Document(result.output_file)
            full_text = "\n".join(p.text for p in doc.paragraphs)

            # Target NIM 12345 replaced with 99999
            self.assertIn("99999", full_text)
            # Other NIM 9123456 MUST STILL EXIST UNTOUCHED!
            self.assertIn("9123456", full_text)
            self.assertIn("REF12345XYZ", full_text)

    def test_engine_conflict_auto_rename(self):
        """Tests that existing output files are auto-renamed gracefully."""
        with tempfile.TemporaryDirectory() as out_temp:
            out_dir = Path(out_temp)
            src = self.docs["doc1"]

            # Run once
            res1 = DocxEngine.process_file(
                src, out_dir, self.old_id, self.new_id, mode=ReplacementMode.BOTH
            )
            self.assertEqual(res1.status, FileProcessStatus.SUCCESS)
            self.assertEqual(res1.output_file.name, src.name)

            # Run second time with AUTO_RENAME
            res2 = DocxEngine.process_file(
                src,
                out_dir,
                self.old_id,
                self.new_id,
                mode=ReplacementMode.BOTH,
                conflict_resolution=ConflictResolution.AUTO_RENAME,
            )
            self.assertEqual(res2.status, FileProcessStatus.SUCCESS)
            self.assertIn("_rev1", res2.output_file.name)
            self.assertTrue(res1.output_file.exists())
            self.assertTrue(res2.output_file.exists())


if __name__ == "__main__":
    unittest.main()
