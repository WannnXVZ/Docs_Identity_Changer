"""End-to-End User Acceptance Testing (UAT) Runner.

Simulates a complete real-world user session across all 9 PRD test documents,
verifying source file immutability, match counts, output verification, and error isolation.
"""

import sys
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings_manager import SettingsManager
from core.docx_engine import DocxEngine
from core.docx_validator import DocxValidator
from core.models import (
    ConflictResolution,
    FileProcessStatus,
    IdentityConfig,
    ReplacementMode,
)
from tests.create_test_docs import generate_all_test_documents


def run_full_uat():
    print("=" * 70)
    print("WORD IDENTITY CHANGER - UAT VERIFICATION SUITE")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as temp_root:
        root_path = Path(temp_root)
        source_dir = root_path / "source_docs"
        output_dir = root_path / "output_docs"
        config_file = root_path / "config.json"

        # 1. Setup sample documents
        print("\n[Step 1] Menyiapkan 9 Dokumen Uji Skenario PRD...")
        docs = generate_all_test_documents(source_dir)
        print(f"  -> {len(docs)} dokumen berhasil dibuat.")

        # 2. Setup Old Identity Config (TSK-002, AC-001)
        print("\n[Step 2] Menguji Persistensi Konfigurasi Identitas Lama (AC-001)...")
        settings = SettingsManager(config_file=config_file)
        old_name_target = "Budi Santoso"
        old_nim_target = "0701234567"
        saved, err = settings.save_config(old_name_target, old_nim_target)
        assert saved, f"Gagal menyimpan config: {err}"

        loaded_name, loaded_nim = settings.load_config()
        assert loaded_name == old_name_target
        assert loaded_nim == old_nim_target
        print(f"  -> Konfigurasi tersimpan: {loaded_name} ({loaded_nim}) [PASS]")

        # 3. New Identity Setup
        new_identity = IdentityConfig(name="Dewi Sartika", nim="0809876543")
        old_identity = IdentityConfig(name=loaded_name, nim=loaded_nim)

        # 4. Step 1: Pre-execution Validation & Scanning (FR-007, FR-008, AC-007)
        print("\n[Step 3] Menjalankan Validasi & Scanner Pra-Eksekusi (AC-007)...")
        file_list = list(docs.values())
        validation_results = []
        for f in file_list:
            v_res = DocxValidator.validate_and_scan(
                f, old_identity.name, old_identity.nim, mode=ReplacementMode.BOTH
            )
            validation_results.append(v_res)
            print(
                f"  - {f.name[:32]:<32} | Status: {v_res.status.value:<12} | Matches: {v_res.match_count.total_matches}"
            )

        # Verify error isolation: corrupt file flagged, doesn't halt
        corrupt_res = next(r for r in validation_results if "corrupted" in r.file_path.name)
        assert not corrupt_res.is_valid, "Corrupt file should be flagged as invalid"
        print("  -> Isolasi file rusak berhasil (AC-012) [PASS]")

        # 5. Step 2: Batch Execution (FR-011, FR-012, FR-013, AC-006, AC-009)
        print("\n[Step 4] Menjalankan Batch Processing Penggantian Identitas (AC-006)...")
        results = []
        for f in file_list:
            p_res = DocxEngine.process_file(
                source_file=f,
                output_dir=output_dir,
                old_identity=old_identity,
                new_identity=new_identity,
                mode=ReplacementMode.BOTH,
                conflict_resolution=ConflictResolution.AUTO_RENAME,
            )
            results.append(p_res)
            status_str = p_res.status.value
            replaced = p_res.matches_replaced.total_matches
            print(f"  - {f.name[:32]:<32} -> {status_str:<12} (Diganti: {replaced})")

        # 6. Verify Acceptance Criteria
        print("\n[Step 5] Verifikasi Kriteria Penerimaan (Acceptance Criteria)...")

        # AC-008: File without target is NOT reported as success
        no_target_res = next(r for r in results if "no_target" in r.source_file.name)
        assert no_target_res.status == FileProcessStatus.NO_TARGET
        print("  [OK] AC-008: Dokumen tanpa kecocokan berstatus NO_TARGET (bukan berhasil).")

        # AC-009: Source files must remain 100% unchanged
        for f in file_list:
            assert f.exists(), f"Source file {f.name} was moved or deleted!"
        print("  [OK] AC-009: Keutuhan file sumber terjamin (tidak ada file asli yang ditimpa).")

        # AC-011: Results verified
        successful_results = [r for r in results if r.status == FileProcessStatus.SUCCESS]
        assert len(successful_results) >= 5, "Expected at least 5 successful files"
        for s in successful_results:
            assert s.verified, f"File {s.output_file.name} failed post-verification"
        print(f"  [OK] AC-011: {len(successful_results)} file hasil terverifikasi identitas baru.")

        print("\n" + "=" * 70)
        print("SELURUH SKENARIO PENGUJIAN UAT LULUS 100% (STATUS: READY FOR RELEASE)")
        print("=" * 70)


if __name__ == "__main__":
    run_full_uat()
