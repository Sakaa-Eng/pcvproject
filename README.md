# Math Bowl Game 🎯

Game edukasi matematika sederhana berbasis OpenCV. Tangkap bola yang berisi jawaban **benar** dari soal yang ditampilkan!

---

## Cara Main

- Soal matematika muncul di bagian atas layar
- 4 bola berisi angka akan jatuh dari atas (1 benar, 3 salah)
- Gerakkan **mangkok** untuk menangkap bola dengan jawaban yang benar
- Hindari menangkap bola yang jawabannya salah

**Kontrol:**
| Tombol | Fungsi |
|---|---|
| `A` / `←` | Gerak mangkok ke kiri |
| `D` / `→` | Gerak mangkok ke kanan |
| `R` | Restart (setelah game over) |
| `Q` | Keluar |

---

## Sistem Penilaian

- ✅ Tangkap jawaban **benar** → **+10 poin**
- ❌ Tangkap jawaban **salah** → **-5 poin** & -1 nyawa
- 💔 Bola benar **terlewat** → -1 nyawa
- Game over saat nyawa habis (3 nyawa)

---

## Cara Menjalankan

```bash
pip install opencv-python numpy
python game.py
```

---

## Struktur Folder

```
Project_Main/
├── game.py          ← file utama (jalankan ini)
├── project.py       ← modul deteksi tangan (OpenCV)
└── tahapan/         ← proses pengembangan dari scratch
    ├── tahap1_bentuk_dasar.py      (objek statis)
    ├── tahap2_gerakan_keyboard.py  (gerakan + keyboard)
    └── tahap3_soal_dan_skor.py     (soal + skor + nyawa)
```

### Folder `tahapan/`

Berisi file-file yang menunjukkan **proses pengembangan bertahap**:

| File | Isi |
|---|---|
| `tahap1` | Gambar lingkaran & kotak sederhana (statis) |
| `tahap2` | Bola berjatuhan, mangkok digerakkan keyboard |
| `tahap3` | Soal matematika, sistem skor & nyawa |

```bash
# Coba tiap tahapan:
python tahapan/tahap1_bentuk_dasar.py
python tahapan/tahap2_gerakan_keyboard.py
python tahapan/tahap3_soal_dan_skor.py
```

---

## Teknologi

- Python 3.10+
- OpenCV (`cv2`)
- NumPy
