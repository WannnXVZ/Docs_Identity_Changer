# Word Identity Changer 📝
**Aplikasi Desktop Otomasi Penggantian Nama & NIM pada Dokumen Microsoft Word (`.docx`)**

Aplikasi ini dirancang khusus untuk mempermudah mahasiswa menyesuaikan identitas (Nama dan NIM) pada dokumen tugas, laporan praktikum, atau template secara *batch* tanpa perlu mengedit satu per satu secara manual.

---

## ⚡ Cara Menjalankan Program (Bisa Langsung Dijalankan!)

Anda memiliki **2 cara** untuk menjalankan aplikasi:

### Cara 1: Langsung Jalankan File Executable (Paling Praktis)
File mandiri sudah dikompilasi ke dalam format `.exe` dan tidak membutuhkan instalasi Python:
1. Buka folder: `dist/`
2. Klik dua kali pada file:
   ```text
   WordIdentityChanger.exe
   ```
   *(Atau jalankan via PowerShell: `.\dist\WordIdentityChanger.exe`)*
3. Jendela aplikasi akan langsung terbuka.

---

### Cara 2: Menjalankan dari Kode Sumber (Python)
Jika Anda menggunakan VS Code atau ingin menjalankan langsung dari kode Python:

1. **Menggunakan Terminal PowerShell**:
   Pastikan berada di direktori proyek `c:\Antigravity\Project\WordIdentityChanger`, lalu jalankan:
   ```powershell
   .\.venv\Scripts\python main.py
   ```

2. **Menggunakan Tombol "Play" / Run di VS Code / Editor**:
   - Di pojok kanan bawah editor, pastikan Python Interpreter terpilih adalah:
     `Python 3.12 (.venv)` (`.\.venv\Scripts\python.exe`).
   - Buka file `main.py`.
   - Klik tombol **Run / Play** (▶) di pojok kanan atas editor.

---

## 🧪 Panduan Cepat Menguji Program (Gunakan Dokumen Uji Siap Pakai)

Di dalam folder `tests/sample_docs/` sudah disediakan **9 dokumen uji nyata** yang mencakup berbagai skenario tugas kuliah:
* `test_doc1_simple_paragraph.docx` (Teks paragraf biasa)
* `test_doc2_split_runs.docx` (Format terpecah: sebagian bold, sebagian miring)
* `test_doc3_in_table.docx` (Identitas di dalam sel tabel laporan)
* `test_doc4_header_footer.docx` (Identitas di running header dan footer)
* `test_doc5_leading_zero.docx` (NIM berawalan nol: `0701234567`)
* `test_doc6_substring_safety.docx` (Uji keamanan: NIM `12345` tidak mengubah `9123456`)
* `test_doc8_multiple.docx` (Kemunculan ganda di berbagai bagian)

### Langkah-Langkah Pengujian:

1. **Jalankan Aplikasi** (`dist/WordIdentityChanger.exe` atau `main.py`).
2. **Atur Identitas Lama (Target yang Dicari)**:
   - Klik tombol **⚙️ Atur Identitas Lama** di pojok kanan atas.
   - Masukkan:
     - **Nama Lama**: `Budi Santoso`
     - **NIM Lama**: `0701234567`
   - Klik **Simpan Konfigurasi**.
   - *Catatan: Pengaturan ini hanya perlu diisi sekali karena disimpan otomatis ke file konfigurasi lokal.*
3. **Masukkan Identitas Baru (Pengganti)**:
   - Pada form utama, masukkan identitas pengganti, misalnya:
     - **Nama Baru**: `Dewi Sartika`
     - **NIM Baru**: `0809876543`
   - Pilih mode penggantian: *Nama dan NIM Sekaligus*.
4. **Pilih File Dokumen**:
   - Klik tombol **+ Tambah File .docx**.
   - Masuk ke folder `tests/sample_docs/`.
   - Pilih satu atau beberapa file (misal: `test_doc1_simple_paragraph.docx`, `test_doc2_split_runs.docx`, `test_doc3_in_table.docx`).
   - Anda juga bisa langsung men-*drag and drop* file `.docx` ke area tabel aplikasi.
5. **Pilih Folder Keluaran**:
   - Folder keluaran default telah terisi (`Documents/WordIdentityChanger_Output`), atau klik **Pilih Folder...** jika ingin menentukan folder lain.
6. **Periksa & Konfirmasi (Pratinjau)**:
   - Klik tombol biru **Periksa & Mulai Penggantian**.
   - Modal **Pratinjau Hasil Validasi** akan muncul, menampilkan jumlah kecocokan nama dan NIM yang ditemukan di tiap dokumen.
   - Klik **Konfirmasi & Mulai Penggantian**.
7. **Lihat Hasil Akhir**:
   - Bilah progres akan berjalan saat dokumen diproses di latar belakang.
   - Setelah selesai, tabel laporan status akhir akan muncul.
   - Klik tombol **📁 Buka Folder Keluaran** untuk langsung membuka hasil dokumen Word di File Explorer dan periksa hasilnya di Microsoft Word!

---

## 🔒 Jaminan Keamanan & Aturan Bisnis (PRD Compliance)

* **Keutuhan Dokumen Asli (BR-005)**: Dokumen sumber tidak akan pernah ditimpa atau dirusak. Hasil selalu disimpan sebagai dokumen baru.
* **Preservasi Format Dokumen (Run-Aware Engine)**: Font, ketebalan (*bold*), kemiringan (*italic*), dan warna dokumen asli tetap utuh walaupun teks identitas terpecah di level XML Word.
* **Preservasi Awalan Nol (BR-004)**: Angka nol di awal NIM (`070...`) dijamin tidak hilang karena diproses secara ketat sebagai teks (*string*).
* **Bebas Salah Sasaran Substring (BR-009)**: Pencocokan teks menggunakan batas kata (`\b`) sehingga NIM pendek tidak akan mengganti bagian dari angka lain.
* **Verifikasi Otomatis (FR-014)**: Setiap dokumen hasil langsung dibaca ulang oleh sistem untuk memastikan identitas baru tersemat dengan sempurna.

---

## 🛠️ Menjalankan Automated Test Suite

Untuk menjalankan seluruh 18 unit test dan skenario integrasi:
```powershell
.\.venv\Scripts\pytest
```

Untuk menjalankan simulasi UAT end-to-end:
```powershell
.\.venv\Scripts\python tests/run_uat_scenarios.py
```
