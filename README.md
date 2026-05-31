# Math Bowl Game

Game menangkap bola matematika pakai OpenCV. Jawab soal yang muncul dengan menangkap bola yang angkanya benar.

## Cara main

- Soal muncul di atas layar
- Bola-bola jatuh dari atas, 1 bola berisi jawaban benar sisanya salah
- Gerakkan mangkok untuk menangkap bola yang benar

Kontrol:
- `a` atau `←` = gerak kiri
- `d` atau `→` = gerak kanan
- `r` = restart
- `q` = keluar

## Jalankan

```
pip install opencv-python numpy
python game.py
```

## File

- `game.py` - file utama game
- `project.py` - modul deteksi tangan (untuk pengembangan selanjutnya)
