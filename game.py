"""
============================================================
  Math Bowl Game
  Versi saat ini: Tahap 3 — Soal Matematika + Skor + Nyawa

  Game sederhana menangkap bola angka yang jatuh.
  Pilih angka yang merupakan jawaban benar dari soal.

  Kontrol:
  a / panah kiri  = gerak mangkok ke kiri
  d / panah kanan = gerak mangkok ke kanan
  r = restart setelah game over
  q = keluar
============================================================
"""
import cv2
import numpy as np
import random

LEBAR  = 640
TINGGI = 480
FONT   = cv2.FONT_HERSHEY_SIMPLEX

RADIUS         = 25
MANGKOK_W      = 80
MANGKOK_H      = 28
KECEPATAN_BOLA = 3
KECEPATAN_MK   = 12
SKOR_BENAR     = 10
SKOR_SALAH     = -5
MAX_NYAWA      = 3


def buat_soal():
    operasi = ['+', '-']
    op = random.choice(operasi)
    a  = random.randint(1, 9)
    b  = random.randint(1, 9)
    if op == '+':
        jawaban = a + b
    else:
        jawaban = a - b
    soal_str = f"{a} {op} {b} = ?"

    # buat 3 jawaban salah
    salah = set()
    while len(salah) < 3:
        d = jawaban + random.randint(1, 8) * random.choice([-1, 1])
        if d != jawaban:
            salah.add(d)

    semua = list(salah) + [jawaban]
    random.shuffle(semua)
    return soal_str, jawaban, semua


class State:
    def __init__(self):
        self.reset()

    def reset(self):
        self.skor      = 0
        self.nyawa     = MAX_NYAWA
        self.game_over = False
        self.mangkok_x = LEBAR // 2
        self.mangkok_y = TINGGI - 80
        self.bola_list = []    # [x, y, nilai, benar(bool), warna]
        self.pesan     = ""    # teks feedback singkat
        self.pesan_t   = 0     # timer pesan
        self._soal_baru()

    def _soal_baru(self):
        soal_str, jawaban, semua = buat_soal()
        self.soal    = soal_str
        self.jawaban = jawaban
        self.bola_list.clear()
        for v in semua:
            x = random.randint(RADIUS + 5, LEBAR - RADIUS - 5)
            y = -RADIUS - random.randint(0, 80)
            benar = (v == jawaban)
            warna = (0, 180, 0) if benar else (0, 0, 200)
            self.bola_list.append([x, y, v, benar, warna])

    def update(self):
        if self.game_over:
            return

        hapus = []
        for i, b in enumerate(self.bola_list):
            b[1] += KECEPATAN_BOLA

            # cek collision dengan mangkok
            mx1 = self.mangkok_x - MANGKOK_W // 2
            mx2 = self.mangkok_x + MANGKOK_W // 2
            my1 = self.mangkok_y
            my2 = self.mangkok_y + MANGKOK_H
            bx, by = int(b[0]), int(b[1])

            if (mx1 - RADIUS < bx < mx2 + RADIUS) and \
               (my1 - RADIUS < by < my2 + RADIUS):
                if b[3]:  # benar
                    self.skor += SKOR_BENAR
                    self.pesan = f"+{SKOR_BENAR} Benar!"
                else:
                    self.skor += SKOR_SALAH
                    self.nyawa -= 1
                    self.pesan = f"{SKOR_SALAH} Salah!"
                self.pesan_t = 40
                hapus.append(i)
                continue

            # bola lewat bawah layar
            if b[1] > TINGGI + RADIUS:
                if b[3]:  # bola benar terlewat
                    self.nyawa -= 1
                    self.pesan = "miss! -1 nyawa"
                    self.pesan_t = 40
                hapus.append(i)

        for i in reversed(hapus):
            self.bola_list.pop(i)

        if self.nyawa <= 0:
            self.game_over = True

        # kalau semua bola habis -> soal baru
        if not self.bola_list:
            self._soal_baru()

        if self.pesan_t > 0:
            self.pesan_t -= 1

    def gambar(self, canvas):
        canvas[:] = 210  # latar abu-abu

        # --- HUD atas ---
        cv2.rectangle(canvas, (0, 0), (LEBAR, 45), (160, 160, 160), -1)
        cv2.putText(canvas, f"Soal: {self.soal}", (10, 30),
                    FONT, 0.9, (0, 0, 0), 2)
        cv2.putText(canvas, f"Skor: {self.skor}", (LEBAR - 130, 22),
                    FONT, 0.55, (0, 0, 0), 1)
        # nyawa: kotak merah sederhana
        for i in range(self.nyawa):
            cv2.rectangle(canvas,
                          (LEBAR - 25 - i * 28, 28),
                          (LEBAR - 8  - i * 28, 42),
                          (0, 0, 220), -1)

        # --- bola ---
        for b in self.bola_list:
            bx, by = int(b[0]), int(b[1])
            warna  = b[4]
            angka  = str(b[2])
            cv2.circle(canvas, (bx, by), RADIUS, warna, -1)
            cv2.circle(canvas, (bx, by), RADIUS, (0, 0, 0), 1)
            (tw, th), _ = cv2.getTextSize(angka, FONT, 0.7, 2)
            cv2.putText(canvas, angka, (bx - tw // 2, by + th // 2),
                        FONT, 0.7, (255, 255, 255), 2)

        # --- mangkok (trapesium sederhana) ---
        mx = self.mangkok_x
        my = self.mangkok_y
        pts = np.array([
            [mx - MANGKOK_W // 2,     my],
            [mx + MANGKOK_W // 2,     my],
            [mx + MANGKOK_W // 2 - 8, my + MANGKOK_H],
            [mx - MANGKOK_W // 2 + 8, my + MANGKOK_H],
        ], np.int32)
        cv2.fillPoly(canvas, [pts], (100, 50, 200))
        cv2.polylines(canvas, [pts], True, (0, 0, 0), 2)

        # --- teks feedback ---
        if self.pesan_t > 0:
            warna_p = (0, 150, 0) if "Benar" in self.pesan else (0, 0, 200)
            cv2.putText(canvas, self.pesan,
                        (LEBAR // 2 - 60, TINGGI // 2 - 20),
                        FONT, 0.9, warna_p, 2)

        # garis bawah
        cv2.line(canvas, (0, TINGGI - 8), (LEBAR, TINGGI - 8), (100, 100, 100), 2)
        cv2.putText(canvas, "a/d = gerak mangkok   |   r = restart   |   q = keluar",
                    (8, TINGGI - 12), FONT, 0.38, (80, 80, 80), 1)

        # game over
        if self.game_over:
            cv2.rectangle(canvas, (100, 150), (LEBAR - 100, 330), (50, 50, 50), -1)
            cv2.rectangle(canvas, (100, 150), (LEBAR - 100, 330), (0, 0, 0), 2)
            cv2.putText(canvas, "GAME OVER", (160, 220),
                        FONT, 1.4, (0, 0, 255), 3)
            cv2.putText(canvas, f"Skor akhir: {self.skor}", (170, 265),
                        FONT, 0.8, (255, 255, 255), 2)
            cv2.putText(canvas, "tekan R untuk main lagi",
                        (150, 305), FONT, 0.55, (200, 200, 200), 1)


def main():
    print("=" * 45)
    print("  Math Bowl Game — Tahap 3")
    print("  a/d = gerak | r = restart | q = keluar")
    print("=" * 45)

    cv2.namedWindow("Math Bowl Game")
    canvas = np.ones((TINGGI, LEBAR, 3), dtype=np.uint8) * 210
    state  = State()

    while True:
        key = cv2.waitKey(30) & 0xFF

        if key == ord("q") or key == 27:
            break

        if not state.game_over:
            if key == ord("a") or key == 81:
                state.mangkok_x = max(MANGKOK_W // 2 + 5,
                                      state.mangkok_x - KECEPATAN_MK)
            elif key == ord("d") or key == 83:
                state.mangkok_x = min(LEBAR - MANGKOK_W // 2 - 5,
                                      state.mangkok_x + KECEPATAN_MK)
            state.update()
        else:
            if key == ord("r"):
                state.reset()

        state.gambar(canvas)
        cv2.imshow("Math Bowl Game", canvas)

    cv2.destroyAllWindows()
    print("Game selesai.")


if __name__ == "__main__":
    main()
