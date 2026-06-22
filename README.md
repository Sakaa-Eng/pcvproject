# Math Bowl - Computer Vision Math Game

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)
![Status](https://img.shields.io/badge/Status-Playable-brightgreen?style=flat)

## Daftar Isi

- [Overview](#overview)
- [Fitur Utama](#fitur-utama)
- [Dependencies](#dependencies)
- [Cara Build dan Run Project](#cara-build-dan-run-project)
- [Cara Bermain](#cara-bermain)
- [Input dan Deteksi](#input-dan-deteksi)
- [Dokumentasi Demo](#dokumentasi-demo)
- [Implementasi Teknis](#implementasi-teknis)
- [Struktur File](#struktur-file)
- [Progress](#progress)
- [Catatan Kalibrasi](#catatan-kalibrasi)

## Overview

Math Bowl adalah mini game edukasi matematika berbasis Computer Vision yang
dibuat menggunakan Python, OpenCV, dan NumPy. Pemain menggerakkan tangan atau
sarung tangan berwarna biru di depan webcam untuk mengontrol objek di dalam
game, lalu menyelesaikan soal matematika yang muncul di layar.

Project ini memiliki dua mode permainan:

- **Tebak Jawaban**: pemain menangkap bola yang berisi jawaban benar dari soal
  penjumlahan atau pengurangan.
- **Tebak Operasi Matematika**: pemain memilih angka dan operator yang dapat
  membentuk ekspresi dengan hasil sesuai target yang diberikan.

Game tetap dapat dimainkan tanpa webcam menggunakan keyboard sebagai fallback.
Jika webcam dan objek biru terdeteksi, kontrol utama akan mengikuti posisi
tangan secara real-time.

## Fitur Utama

- **Real-time webcam input** menggunakan `cv2.VideoCapture`.
- **Blue glove tracking** memakai segmentasi warna HSV.
- **Noise filtering** dengan Gaussian blur, threshold, erode, dan dilate.
- **Contour validation** berdasarkan luas contour dan solidity.
- **Palm center tracking** memakai distance transform pada mask tangan.
- **Smoothing posisi tangan** agar gerakan kursor lebih stabil.
- **Main menu interaktif** dengan pilihan start, quit, dan pemilihan mode.
- **Dua mode gameplay matematika** dalam satu project.
- **Keyboard fallback** ketika kamera atau sarung tangan biru tidak terdeteksi.
- **Score, nyawa, pesan feedback, restart, dan game over screen**.
- **Preview kamera kecil** di area game untuk membantu melihat status deteksi.
- **Musik opsional** dari folder `music/` jika `pygame` tersedia.

## Dependencies

Dependency utama:

- Python 3.10 atau lebih baru
- OpenCV Python
- NumPy
- Webcam laptop atau kamera eksternal

Dependency opsional:

- Pygame, hanya untuk memutar musik background dari folder `music/`

Install dependency utama:

```bash
pip install opencv-python numpy
```

Install dependency lengkap dengan musik:

```bash
pip install opencv-python numpy pygame
```

## Cara Build dan Run Project

Project ini tidak membutuhkan proses compile. Jalankan langsung dengan Python.

1. Clone repository:

   ```bash
   git clone https://github.com/Sakaa-Eng/pcvproject.git
   cd pcvproject
   ```

2. Install dependency:

   ```bash
   pip install opencv-python numpy
   ```

3. Jalankan menu utama:

   ```bash
   python main_menu.py
   ```

4. Pilih mode game dari menu yang muncul.

Game juga bisa dijalankan langsung per mode:

```bash
python game.py
python game_mode2.py
```

Untuk menguji deteksi sarung tangan biru saja:

```bash
python project.py
```

## Cara Bermain

### Main Menu

Saat program dijalankan lewat `main_menu.py`, pemain masuk ke menu utama.

Kontrol menu:

| Input | Fungsi |
|-------|--------|
| `W` / panah atas | Pindah pilihan ke atas |
| `S` / panah bawah | Pindah pilihan ke bawah |
| `Enter` / `Space` | Konfirmasi pilihan |
| `Esc` | Kembali dari pemilihan mode atau keluar dari menu utama |
| `Q` | Keluar dari menu utama |

### Mode 1: Tebak Jawaban

Pada mode ini, soal matematika muncul di bagian atas layar. Beberapa bola
berisi pilihan jawaban akan jatuh dari atas. Pemain harus menggerakkan mangkok
untuk menangkap bola dengan jawaban yang benar.

Aturan mode 1:

- Jawaban benar menambah skor.
- Jawaban salah mengurangi skor dan nyawa.
- Jika bola jawaban benar terlewat, nyawa berkurang.
- Game over terjadi saat nyawa habis.

Kontrol mode 1:

| Input | Fungsi |
|-------|--------|
| Sarung tangan biru | Menggerakkan mangkok secara horizontal |
| `A` / panah kiri | Gerak ke kiri jika tangan tidak terdeteksi |
| `D` / panah kanan | Gerak ke kanan jika tangan tidak terdeteksi |
| `R` | Restart setelah game over |
| `Q` / `Esc` | Keluar dari game |

### Mode 2: Tebak Operasi Matematika

Pada mode ini, game menampilkan target hasil. Pemain harus memilih bola angka
dan operator sehingga membentuk ekspresi matematika yang hasilnya sama dengan
target tersebut.

Contoh target:

```text
Nilai berapa yg hasilnya 7?
```

Pemain dapat menyentuh bola berlabel angka dan operator, misalnya `3 + 4`.
Jika ekspresi yang dipilih benar, skor bertambah dan soal baru dibuat.

Aturan mode 2:

- Pemain memilih bola dengan menyentuhkan kursor tangan ke bola.
- Urutan pilihan ditampilkan pada bola yang sudah disentuh.
- Jika ekspresi benar, pemain mendapat skor.
- Jika terlalu banyak pilihan dan belum ada ekspresi benar, nyawa berkurang.
- Game over terjadi saat nyawa habis.

Kontrol mode 2:

| Input | Fungsi |
|-------|--------|
| Sarung tangan biru | Menggerakkan kursor tangan pada sumbu X dan Y |
| `W` / panah atas | Gerak ke atas jika tangan tidak terdeteksi |
| `S` / panah bawah | Gerak ke bawah jika tangan tidak terdeteksi |
| `A` / panah kiri | Gerak ke kiri jika tangan tidak terdeteksi |
| `D` / panah kanan | Gerak ke kanan jika tangan tidak terdeteksi |
| `R` | Reset pilihan atau restart setelah game over |
| `Q` / `Esc` | Keluar dari game |

## Input dan Deteksi

Pipeline deteksi tangan berada di `project.py`:

1. Frame webcam dibaca dan dibalik secara horizontal agar gerakan terasa natural.
2. Frame dikonversi dari BGR ke HSV.
3. Warna biru dideteksi memakai rentang `blue_lower` dan `blue_upper`.
4. Mask dibersihkan dengan blur, threshold, erode, dan dilate.
5. Contour eksternal dicari dari mask.
6. Contour difilter berdasarkan `MIN_AREA`, `MAX_AREA`, dan `MIN_SOLID`.
7. Contour valid terbesar dianggap sebagai sarung tangan atau objek input.
8. Area contour diubah menjadi mask terisi.
9. `cv2.distanceTransform` dipakai untuk mencari titik pusat telapak.
10. Koordinat tangan dihaluskan dengan konstanta `SMOOTH`.
11. Game memakai `hand_x` dan `hand_y` sebagai input kontrol.

Jika tangan tidak terdeteksi, game otomatis memakai kontrol keyboard.

## Dokumentasi Demo

Folder dokumentasi demo sudah disiapkan di dalam `docs/`.

```text
docs/
|-- screenshots/     # Simpan foto atau screenshot demo di sini
`-- videos/          # Simpan video demo gameplay di sini
```

### Foto atau Screenshot

Tambahkan screenshot gameplay ke folder `docs/screenshots/`. Rekomendasi file
yang bisa dimasukkan:

| Dokumentasi | Lokasi File |
|-------------|-------------|
| Tampilan main menu | `docs/screenshots/main-menu.png` |
| Mode tebak jawaban | `docs/screenshots/mode-tebak-jawaban.png` |
| Mode tebak operasi matematika | `docs/screenshots/mode-tebak-operasi.png` |
| Deteksi sarung tangan biru | `docs/screenshots/deteksi-sarung-tangan.png` |
| Tampilan game over | `docs/screenshots/game-over.png` |

Setelah file dimasukkan, gambar dapat ditampilkan di README dengan format:

```md
![Main Menu](docs/screenshots/main-menu.png)
![Mode Tebak Jawaban](docs/screenshots/mode-tebak-jawaban.png)
![Mode Tebak Operasi](docs/screenshots/mode-tebak-operasi.png)
![Deteksi Sarung Tangan](docs/screenshots/deteksi-sarung-tangan.png)
```

### Video Demo

Tambahkan video demo ke folder `docs/videos/`. Rekomendasi file yang bisa
dimasukkan:

| Dokumentasi | Lokasi File |
|-------------|-------------|
| Demo gameplay lengkap | `docs/videos/demo-math-bowl.mp4` |
| Demo mode tebak jawaban | `docs/videos/demo-mode-tebak-jawaban.mp4` |
| Demo mode tebak operasi | `docs/videos/demo-mode-tebak-operasi.mp4` |

Setelah video dimasukkan, tautkan video di README dengan format:

```md
[Lihat Demo Gameplay](docs/videos/demo-math-bowl.mp4)
```

Jika video diunggah melalui GitHub user attachments, tautan video juga bisa
ditempel langsung pada bagian ini.

## Implementasi Teknis

Project ini dibagi menjadi beberapa modul kecil agar menu, gameplay, dan
Computer Vision lebih mudah dikembangkan.

### `main_menu.py`

File ini menjadi entry point utama project. Modul ini membuat jendela menu
dengan OpenCV, menangani navigasi pilihan, lalu menjalankan mode game yang
dipilih pemain.

Alur implementasi:

1. Membuat canvas menu berukuran 640 x 480.
2. Menampilkan tombol `START` dan `QUIT`.
3. Setelah `START`, menampilkan pilihan mode game.
4. Menjalankan `game.py` untuk mode tebak jawaban.
5. Menjalankan `game_mode2.py` untuk mode tebak operasi matematika.

### `game.py`

File ini berisi mode **Tebak Jawaban**. Soal matematika dibuat secara acak,
lalu beberapa bola jawaban dijatuhkan dari atas layar. Pemain harus menangkap
bola yang berisi jawaban benar.

Komponen implementasi:

- `buat_soal()` membuat soal penjumlahan atau pengurangan beserta pilihan
  jawaban.
- Class `Game` menyimpan skor, nyawa, posisi mangkok, daftar bola, dan status
  game over.
- `update()` mengatur gerakan bola, collision dengan mangkok, pengurangan
  nyawa, dan pergantian soal.
- `draw()` menggambar UI, soal, bola, mangkok, skor, nyawa, pesan feedback, dan
  game over screen.
- `buka_kamera()` mencari webcam aktif dari beberapa index dan backend.

### `game_mode2.py`

File ini berisi mode **Tebak Operasi Matematika**. Pemain memilih bola angka
dan operator untuk membentuk ekspresi yang menghasilkan target tertentu.

Komponen implementasi:

- `buat_soal()` membuat target hasil dari operasi matematika acak.
- `buat_bola()` membuat bola angka, operator benar, dan distraktor.
- Class `Bola` menyimpan posisi, label, status pilihan, dan urutan sentuhan.
- Class `Game` menyimpan ekspresi yang sedang dipilih pemain.
- Method `_cek()` mencari pola `angka operator angka`, menghitung hasilnya, dan
  menentukan apakah jawaban benar.

### `project.py`

File ini menjadi modul Computer Vision untuk mendeteksi sarung tangan atau
objek berwarna biru.

Komponen implementasi:

- `blue_mask()` mengubah frame ke HSV dan membuat mask warna biru.
- `clean_mask()` membersihkan noise dengan blur, threshold, erode, dan dilate.
- `valid_contour()` memfilter contour berdasarkan area dan solidity.
- `detect_hand()` mengambil contour valid terbesar, mencari pusat telapak
  dengan distance transform, lalu mengembalikan koordinat tangan.
- `draw_detection()` menggambar bounding box, pusat tangan, radius telapak, dan
  status deteksi untuk debugging.
- `calibrate()` mengubah rentang HSV berdasarkan area tengah frame.

### Integrasi Kamera dan Keyboard

Kedua mode game memakai `detect_hand(frame)` dari `project.py`. Jika tangan
terdeteksi, koordinat tangan dipakai sebagai kontrol utama. Jika tidak
terdeteksi atau webcam tidak tersedia, kontrol keyboard tetap bisa digunakan
agar game masih dapat dimainkan.

## Struktur File

```text
pcvproject/
|-- docs/
|   |-- README.md        # Panduan penyimpanan dokumentasi demo
|   |-- screenshots/     # Tempat menyimpan foto atau screenshot demo
|   |   `-- .gitkeep
|   `-- videos/          # Tempat menyimpan video demo
|       `-- .gitkeep
|-- README.md            # Dokumentasi utama project
|-- main_menu.py         # Entry point menu utama dan pemilihan mode
|-- game.py              # Mode 1: menangkap bola jawaban benar
|-- game_mode2.py        # Mode 2: menyusun angka dan operator
`-- project.py           # Modul deteksi sarung tangan biru dengan OpenCV
```

Folder opsional:

```text
pcvproject/
`-- music/           # Isi dengan file .mp3, .wav, atau .ogg untuk BGM
```

Jika folder `music/` belum ada, `game.py` akan mencoba membuat folder tersebut
saat mode 1 dijalankan. Pada mode 2, musik hanya diputar jika folder dan file
musik sudah tersedia.

## Progress

| Status | Keterangan |
|--------|------------|
| [x] | Main menu dengan pilihan start dan quit |
| [x] | Pemilihan dua mode permainan |
| [x] | Mode tebak jawaban dengan bola jatuh |
| [x] | Mode susun angka dan operator |
| [x] | Deteksi objek biru berbasis HSV |
| [x] | Validasi contour dan smoothing posisi tangan |
| [x] | Keyboard fallback ketika kamera tidak tersedia |
| [x] | Score, nyawa, restart, dan game over |
| [x] | Preview kamera kecil di layar game |
| [x] | Musik background opsional dengan `pygame` |

## Catatan Kalibrasi

Jika sarung tangan biru belum terdeteksi stabil, jalankan:

```bash
python project.py
```

Gunakan kontrol berikut pada jendela deteksi:

| Input | Fungsi |
|-------|--------|
| `C` | Kalibrasi warna biru dari area tengah frame |
| `D` | Toggle tampilan mask |
| `Q` / `Esc` | Keluar |

Nilai yang dapat diubah di `project.py`:

- `blue_lower` dan `blue_upper`: batas bawah dan atas warna biru dalam HSV.
- `MIN_AREA`: luas minimum contour agar noise kecil tidak dianggap tangan.
- `MAX_AREA`: luas maksimum contour agar area terlalu besar tidak dipilih.
- `MIN_SOLID`: batas kepadatan contour terhadap convex hull.
- `SMOOTH`: tingkat smoothing koordinat tangan.

Tips agar deteksi lebih stabil:

- Gunakan sarung tangan atau objek berwarna biru yang cukup kontras.
- Hindari background dengan warna biru yang mirip.
- Pastikan cahaya ruangan cukup terang dan tidak berubah drastis.
- Tekan `C` saat objek biru berada di tengah frame untuk kalibrasi cepat.
