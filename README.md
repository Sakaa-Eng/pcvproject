# Math Bowl Game

Game edukasi matematika interaktif yang dibangun menggunakan **Pure OpenCV dan NumPy**, tanpa framework game eksternal. Seluruh proses rendering, game loop, deteksi input, dan computer vision dikerjakan sepenuhnya menggunakan OpenCV dan NumPy.

> **Mata Kuliah**: Pengolahan Citra dan Video (PCV)

---

## Deskripsi Proyek

Math Bowl adalah game menangkap bola matematika yang menyajikan dua mode permainan berbeda. Pada kedua mode, pemain berinteraksi dengan antarmuka yang dirender secara real-time oleh OpenCV di atas canvas NumPy berukuran 640x480 piksel.

Mode pertama (Tangkap Bola) menampilkan soal aritmatika di layar, lalu menjatuhkan bola-bola dari atas layar. Pemain menggerakkan mangkok untuk menangkap bola yang berisi jawaban benar. Mode kedua (Susun Ekspresi) membalik mekanik tersebut: bola-bola tidak bergerak, namun masing-masing berisi satu komponen ekspresi matematika (angka atau operator), dan pemain harus menyentuhnya secara berurutan untuk membentuk ekspresi yang menghasilkan nilai target.

Kedua mode mendukung input ganda: keyboard sebagai fallback, dan kamera webcam sebagai input primer melalui deteksi tangan berbasis Computer Vision.

---

## Identitas

| Atribut | Keterangan |
|---|---|
| Repositori | https://github.com/Sakaa-Eng/pcvproject |
| Bahasa | Python 3.8+ |
| Library Utama | OpenCV, NumPy |
| Library Opsional | pygame (audio saja) |
| Ukuran Canvas | 640 x 480 piksel |

---

## Struktur Proyek

```text
pcvproject/
├── project.py       -- Modul computer vision: deteksi tangan berbasis HSV masking
├── game.py          -- Mode 1: Tangkap Bola (bola jatuh, mangkok bergerak horizontal)
├── game_mode2.py    -- Mode 2: Susun Ekspresi (bola statis, kursor tangan bergerak bebas)
├── main_menu.py     -- Menu utama berbasis OpenCV (pilihan mode dengan keyboard)
├── music/           -- Direktori opsional berisi file audio (.mp3 / .wav / .ogg)
└── README.md
```

---

## Arsitektur Sistem

Proyek ini terdiri dari empat modul dengan peran masing-masing:

**`project.py` — Modul Computer Vision**

Modul ini bertanggung jawab atas seluruh pipeline deteksi tangan. Tidak bergantung pada library machine learning; seluruh proses dikerjakan secara manual menggunakan operasi citra OpenCV.

**`game.py` — Mode 1**

Mengimplementasikan logika game Tangkap Bola. Mengelola siklus soal, pergerakan bola, deteksi tabrakan dengan mangkok, sistem skor, dan rendering seluruh elemen ke canvas.

**`game_mode2.py` — Mode 2**

Mengimplementasikan logika game Susun Ekspresi. Mengelola bola-bola statis berisi label, pergerakan kursor tangan, deteksi sentuhan berdasarkan jarak Euclidean, dan validasi ekspresi matematika.

**`main_menu.py` — Menu Utama**

Menampilkan layar menu dengan dua tombol (Mode 1 dan Mode 2) yang dirender menggunakan OpenCV. Navigasi menggunakan tombol `W`/`S` dan `Enter`.

---

## Pipeline Computer Vision (project.py)

Deteksi tangan dilakukan melalui segmentasi warna biru (sarung tangan biru) dalam ruang warna HSV. Pipeline berjalan pada setiap frame kamera secara real-time.

### 1. Konversi Ruang Warna

Frame BGR dari kamera dikonversi ke HSV menggunakan `cv2.cvtColor`. Ruang warna HSV lebih robust terhadap perubahan pencahayaan dibanding BGR untuk keperluan segmentasi warna.

Default range warna biru yang digunakan:

```
H: 95 - 135
S: 60 - 255
V: 40 - 255
```

### 2. Kalibrasi Warna (Opsional)

Fungsi `calibrate(frame, cx, cy, size=30)` memungkinkan pemain mengkalibrasi range warna secara manual. Fungsi ini mengambil ROI berukuran 60x60 piksel di sekitar titik (cx, cy), menghitung rata-rata nilai H dan S dari region tersebut, lalu memperbarui `blue_lower` dan `blue_upper` dengan toleransi:

```
Toleransi H : +-15
Toleransi S : +-60
```

### 3. Pembersihan Mask (Morfologi)

Mask biner hasil `cv2.inRange` diproses melalui tiga tahap:

1. **Gaussian Blur** (kernel 5x5) untuk mengurangi noise sebelum threshold
2. **Erosi** (ellipse kernel 5x5, 1 iterasi) untuk menghilangkan noise kecil dan memisahkan komponen yang hampir menyentuh
3. **Dilasi** (ellipse kernel 11x11, 3 iterasi) untuk mengisi lubang di dalam area tangan dan mengembalikan ukurannya

### 4. Deteksi Kontur dan Validasi

Kontur diekstrak dari mask bersih menggunakan `cv2.findContours`. Setiap kontur divalidasi berdasarkan dua kriteria:

- **Area**: harus berada di antara `MIN_AREA = 3000` dan `MAX_AREA = 80000` piksel
- **Solidity**: rasio `area / convex_hull_area` harus >= `MIN_SOLID = 0.35`. Kriteria ini memastikan kontur cukup solid dan bukan noise berbentuk tidak beraturan.

### 5. Posisi Tangan dan Smoothing

Centroid tangan dihitung menggunakan image moments (`cv2.moments`). Koordinat mentah (cx_raw, cy_raw) kemudian diperhalus menggunakan exponential moving average dengan faktor `SMOOTH = 0.40`:

```
sx = sx + 0.40 * (cx_raw - sx)
sy = sy + 0.40 * (cy_raw - sy)
```

Smoothing ini mencegah gerakan cursor yang terlalu kasar akibat noise deteksi antar frame.

### 6. Output Fungsi detect_hand

Fungsi `detect_hand(frame)` mengembalikan dictionary berisi:

| Key | Tipe | Keterangan |
|---|---|---|
| `hand_detected` | bool | True jika tangan terdeteksi |
| `hand_x` | int | Koordinat X centroid tangan (dalam skala canvas 640px) |
| `hand_y` | int | Koordinat Y centroid tangan (dalam skala canvas 480px) |
| `palm_radius` | float | Estimasi radius area tangan dari bounding box |
| `bbox` | tuple | Bounding box (x, y, w, h) dari kontur tangan |
| `mask` | ndarray | Mask biner hasil proses morfologi |

---

## Mode 1: Tangkap Bola (game.py)

### Mekanik Permainan

Setiap ronde menampilkan satu soal aritmatika (penjumlahan atau pengurangan, operand 1-9). Empat bola jatuh dari atas layar, masing-masing berisi satu angka: satu berisi jawaban benar, tiga berisi distraktor yang dibuat dari `jawaban + random_offset * random_sign` sehingga berbeda dari jawaban namun tetap dalam rentang yang masuk akal.

Layar dibagi menjadi 4 zona horizontal yang sama lebar. Setiap bola ditempatkan secara acak di dalam satu zona yang berbeda untuk mencegah bola saling bertumpuk. Bola ke-i dimulai dari posisi Y = `-RADIUS - i * 60`, sehingga bola muncul secara bergantian (tidak serentak).

### Deteksi Tabrakan

Tabrakan antara bola dan mangkok diperiksa setiap frame menggunakan AABB (Axis-Aligned Bounding Box). Mangkok berukuran `80 x 28` piksel. Kondisi tabrakan:

```
(mk_x - 40 - RADIUS) < bola_x < (mk_x + 40 + RADIUS)
AND
(mk_y - RADIUS) < bola_y < (mk_y + 28 + RADIUS)
```

### Kontrol Mangkok

| Input | Aksi |
|---|---|
| `A` atau panah kiri | Gerak kiri (kecepatan: 12 px/frame) |
| `D` atau panah kanan | Gerak kanan (kecepatan: 12 px/frame) |

Jika kamera aktif dan tangan terdeteksi, posisi X tangan yang dideteksi `project.py` digunakan langsung sebagai posisi mangkok.

### Sistem Skor dan Nyawa

| Kondisi | Akibat |
|---|---|
| Tangkap bola benar | +10 poin |
| Tangkap bola salah | -5 poin, -1 nyawa |
| Bola benar lolos ke bawah | -1 nyawa |
| Nyawa mencapai 0 | Game Over |

Nyawa awal: 3. Setelah semua bola habis (tertangkap atau lolos), soal baru digenerate secara otomatis.

---

## Mode 2: Susun Ekspresi (game_mode2.py)

### Mekanik Permainan

Layar menampilkan pertanyaan berupa nilai target (contoh: "Nilai berapa yg hasilnya 7?"). Tujuh bola statis tersebar di layar dalam grid 4x2, berisi label campuran: angka pertama (a), operator, angka kedua (b), tiga distraktor angka acak, dan satu distraktor operator.

Pemain menggerakkan kursor tangan untuk menyentuh bola-bola secara berurutan guna membentuk ekspresi matematika yang valid.

### Logika Validasi Ekspresi

Setiap kali bola disentuh, labelnya ditambahkan ke dalam daftar `ekspresi`. Fungsi `_cek()` kemudian mencari pola `angka - operator - angka` dalam ekspresi yang sudah terkumpul menggunakan sliding window dengan panjang 3. Jika hasilnya sama dengan nilai target, ronde dinyatakan benar dan soal baru digenerate.

Jika ekspresi sudah mencapai 5 item tanpa ada pola yang valid, pemain kehilangan satu nyawa dan pilihan direset.

### Deteksi Sentuhan Bola

Berbeda dengan Mode 1 yang menggunakan AABB, Mode 2 menggunakan jarak Euclidean:

```
dist = sqrt((tangan_x - bola_x)^2 + (tangan_y - bola_y)^2)
Sentuhan terjadi jika dist < RADIUS_BOLA + 12
```

### Kontrol Kursor Tangan

| Input | Aksi |
|---|---|
| `W` atau panah atas | Kursor naik |
| `S` atau panah bawah | Kursor turun |
| `A` atau panah kiri | Kursor kiri |
| `D` atau panah kanan | Kursor kanan |
| `R` | Reset pilihan saat ini |

Jika kamera aktif dan tangan terdeteksi, posisi kursor diperbarui menggunakan interpolasi linear:

```
tangan_x += (hand_x - tangan_x) * 0.5
tangan_y += (hand_y - tangan_y) * 0.5
```

Faktor 0.5 menghasilkan gerakan kursor yang responsif namun tetap halus.

---

## Menu Utama (main_menu.py)

Menu utama dirender menggunakan OpenCV pada canvas yang sama. Terdapat dua tombol: **START** (memuat Mode 1) dan **QUIT**. Navigasi dilakukan dengan `W`/`S` untuk berpindah pilihan dan `Enter` untuk mengkonfirmasi.

Kedua mode game diimpor sebagai fungsi (`jalankan_game1`, `jalankan_game2`) dan dijalankan langsung dari proses yang sama tanpa subprocess.

---

## Sistem Audio

Kedua mode game mencoba memuat file audio dari direktori `music/` di direktori kerja. Format yang didukung: `.mp3`, `.wav`, `.ogg`. Jika direktori tidak ada atau tidak berisi file audio, game tetap berjalan tanpa audio. Jika `pygame` tidak terinstall, seluruh fitur audio dilewati secara otomatis melalui blok `try/except` di awal modul.

Audio dimainkan secara looping (`play(-1)`) dengan volume 0.5.

---

## Preview Kamera

Pada Mode 2, frame kamera yang sedang diproses ditampilkan sebagai miniatur 160x120 piksel di pojok kanan bawah canvas. Bounding box tangan yang terdeteksi digambar di atas miniatur ini menggunakan kotak hijau. Status deteksi ("tangan OK" atau "tangan -") ditampilkan di atas miniatur.

---

## Cara Menjalankan

### Instalasi Dependensi

```bash
pip install opencv-python numpy
```

Untuk dukungan audio (opsional):

```bash
pip install pygame
```

### Menjalankan Game

```bash
# Via menu utama (direkomendasikan)
python main_menu.py

# Langsung ke Mode 1
python game.py

# Langsung ke Mode 2
python game_mode2.py
```

### Persyaratan Hardware

- Webcam (opsional, game tetap bisa dimainkan dengan keyboard)
- Sarung tangan berwarna biru untuk deteksi tangan yang optimal
- Python 3.8 atau lebih baru

---

## Konstanta Konfigurasi

### Mode 1 (game.py)

| Konstanta | Nilai | Keterangan |
|---|---|---|
| `W`, `H` | 640, 480 | Dimensi canvas |
| `RADIUS` | 25 | Radius bola dalam piksel |
| `MK_W`, `MK_H` | 80, 28 | Dimensi mangkok |
| `SPEED` | 3 | Kecepatan jatuh bola (px/frame) |
| `MK_SPEED` | 12 | Kecepatan gerak mangkok (px/frame) |
| `POIN_BENAR` | +10 | Poin untuk jawaban benar |
| `POIN_SALAH` | -5 | Poin untuk jawaban salah |
| `NYAWA` | 3 | Jumlah nyawa awal |

### Mode 2 (game_mode2.py)

| Konstanta | Nilai | Keterangan |
|---|---|---|
| `TANGAN_SPEED` | 6 | Kecepatan kursor keyboard (px/frame) |
| `RADIUS_BOLA` | 22 | Radius bola dalam piksel |
| `NYAWA` | 3 | Jumlah nyawa awal |
| `POIN` | 10 | Poin untuk ekspresi benar |

### Computer Vision (project.py)

| Konstanta | Nilai | Keterangan |
|---|---|---|
| `blue_lower` | [95, 60, 40] | Batas bawah HSV warna biru |
| `blue_upper` | [135, 255, 255] | Batas atas HSV warna biru |
| `MIN_AREA` | 3000 | Area minimum kontur tangan (piksel) |
| `MAX_AREA` | 80000 | Area maksimum kontur tangan (piksel) |
| `MIN_SOLID` | 0.35 | Rasio solidity minimum kontur |
| `SMOOTH` | 0.40 | Faktor smoothing exponential moving average |

---

## Konsep Computer Vision yang Diterapkan

- **Color Segmentation**: Segmentasi berbasis HSV untuk memisahkan objek dari latar berdasarkan warna
- **Morphological Operations**: Erosi dan dilasi untuk membersihkan mask biner
- **Contour Detection**: Ekstraksi kontur menggunakan `cv2.findContours`
- **Image Moments**: Kalkulasi centroid objek menggunakan `cv2.moments`
- **Convex Hull**: Digunakan dalam validasi solidity kontur
- **Exponential Moving Average**: Smoothing posisi tangan antar frame
- **Pure OpenCV Rendering**: Seluruh antarmuka game dibangun menggunakan primitif OpenCV (`rectangle`, `circle`, `putText`, `line`, `fillPoly`)
