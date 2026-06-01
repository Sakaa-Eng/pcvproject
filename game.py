import cv2
import numpy as np
import random
import os

try:
    import pygame
    pygame.mixer.init()
    MUSIK = True
except:
    MUSIK = False


W = 640
H = 480
FONT = cv2.FONT_HERSHEY_SIMPLEX

RADIUS = 25
MK_W = 80
MK_H = 28
SPEED = 3
MK_SPEED = 12
POIN_BENAR = 10
POIN_SALAH = -5
NYAWA = 3


def buat_soal():
    op = random.choice(['+', '-'])
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    jawaban = a + b if op == '+' else a - b
    soal = f"{a} {op} {b} = ?"

    salah = set()
    while len(salah) < 3:
        d = jawaban + random.randint(1, 8) * random.choice([-1, 1])
        if d != jawaban:
            salah.add(d)

    pilihan = list(salah) + [jawaban]
    random.shuffle(pilihan)
    return soal, jawaban, pilihan


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.skor = 0
        self.nyawa = NYAWA
        self.over = False
        self.mk_x = W // 2
        self.mk_y = H - 80
        self.bola = []
        self.pesan = ""
        self.pesan_timer = 0
        self.soal_baru()

    def soal_baru(self):
        soal, jwb, pilihan = buat_soal()
        self.soal = soal
        self.jwb = jwb
        self.bola.clear()

        # bagi layar jadi 4 zona biar gak dempet
        zone_w = W // 4
        zona = list(range(4))
        random.shuffle(zona)

        for i, v in enumerate(pilihan):
            z = zona[i]
            x_min = z * zone_w + RADIUS + 5
            x_max = (z + 1) * zone_w - RADIUS - 5
            x = random.randint(x_min, x_max)
            # y disebar biar muncul bergantian bukan barengan
            y = -RADIUS - i * 60
            benar = (v == jwb)
            warna = (0, 180, 0) if benar else (0, 0, 200)
            self.bola.append([x, y, v, benar, warna])


    def update(self):
        if self.over:
            return

        hapus = []
        for i, b in enumerate(self.bola):
            b[1] += SPEED

            mx1 = self.mk_x - MK_W // 2
            mx2 = self.mk_x + MK_W // 2
            my1 = self.mk_y
            my2 = self.mk_y + MK_H
            bx, by = int(b[0]), int(b[1])

            if (mx1 - RADIUS < bx < mx2 + RADIUS) and (my1 - RADIUS < by < my2 + RADIUS):
                if b[3]:
                    self.skor += POIN_BENAR
                    self.pesan = "+10 Benar!"
                else:
                    self.skor += POIN_SALAH
                    self.nyawa -= 1
                    self.pesan = "-5 Salah!"
                self.pesan_timer = 40
                hapus.append(i)
                continue

            if b[1] > H + RADIUS:
                if b[3]:
                    self.nyawa -= 1
                    self.pesan = "miss!"
                    self.pesan_timer = 40
                hapus.append(i)

        for i in reversed(hapus):
            self.bola.pop(i)

        if self.nyawa <= 0:
            self.over = True

        if not self.bola:
            self.soal_baru()

        if self.pesan_timer > 0:
            self.pesan_timer -= 1

    def draw(self, canvas):
        canvas[:] = 210

        cv2.rectangle(canvas, (0, 0), (W, 45), (160, 160, 160), -1)
        cv2.putText(canvas, f"Soal: {self.soal}", (10, 30), FONT, 0.9, (0, 0, 0), 2)
        cv2.putText(canvas, f"Skor: {self.skor}", (W - 130, 22), FONT, 0.55, (0, 0, 0), 1)

        for i in range(self.nyawa):
            cv2.rectangle(canvas, (W - 25 - i * 28, 28), (W - 8 - i * 28, 42), (0, 0, 220), -1)

        for b in self.bola:
            bx, by = int(b[0]), int(b[1])
            cv2.circle(canvas, (bx, by), RADIUS, b[4], -1)
            cv2.circle(canvas, (bx, by), RADIUS, (0, 0, 0), 1)
            teks = str(b[2])
            (tw, th), _ = cv2.getTextSize(teks, FONT, 0.7, 2)
            cv2.putText(canvas, teks, (bx - tw // 2, by + th // 2), FONT, 0.7, (255, 255, 255), 2)

        mx, my = self.mk_x, self.mk_y
        pts = np.array([
            [mx - MK_W // 2, my],
            [mx + MK_W // 2, my],
            [mx + MK_W // 2 - 8, my + MK_H],
            [mx - MK_W // 2 + 8, my + MK_H],
        ], np.int32)
        cv2.fillPoly(canvas, [pts], (100, 50, 200))
        cv2.polylines(canvas, [pts], True, (0, 0, 0), 2)

        if self.pesan_timer > 0:
            warna_p = (0, 150, 0) if "Benar" in self.pesan else (0, 0, 200)
            cv2.putText(canvas, self.pesan, (W // 2 - 60, H // 2 - 20), FONT, 0.9, warna_p, 2)

        cv2.line(canvas, (0, H - 8), (W, H - 8), (100, 100, 100), 2)
        cv2.putText(canvas, "a/d = gerak  |  r = restart  |  q = keluar",
                    (8, H - 12), FONT, 0.38, (80, 80, 80), 1)

        if self.over:
            cv2.rectangle(canvas, (100, 150), (W - 100, 330), (50, 50, 50), -1)
            cv2.rectangle(canvas, (100, 150), (W - 100, 330), (0, 0, 0), 2)
            cv2.putText(canvas, "GAME OVER", (160, 220), FONT, 1.4, (0, 0, 255), 3)
            cv2.putText(canvas, f"Skor: {self.skor}", (210, 268), FONT, 0.8, (255, 255, 255), 2)
            cv2.putText(canvas, "tekan R untuk main lagi", (155, 308), FONT, 0.52, (200, 200, 200), 1)


def cari_lagu(folder="music"):
    if not MUSIK:
        return None
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"folder '{folder}' dibuat, masukkan file musik (.mp3/.wav/.ogg) ke sana")
        return None
    ekstensi = ('.mp3', '.wav', '.ogg')
    files = [f for f in os.listdir(folder) if f.lower().endswith(ekstensi)]
    if not files:
        print(f"tidak ada file musik di folder '{folder}'")
        return None
    pilihan = random.choice(files)
    return os.path.join(folder, pilihan)


def putar_musik(path):
    if not MUSIK or path is None:
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)  # loop terus
        print(f"memutar: {os.path.basename(path)}")
    except Exception as e:
        print(f"gagal putar musik: {e}")


def main():
    lagu = cari_lagu("music")
    putar_musik(lagu)
    nama_lagu = os.path.basename(lagu) if lagu else ""

    cv2.namedWindow("Math Bowl")
    canvas = np.ones((H, W, 3), dtype=np.uint8) * 210
    game = Game()

    while True:
        key = cv2.waitKey(30) & 0xFF

        if key == ord("q") or key == 27:
            break

        if not game.over:
            if key == ord("a") or key == 81:
                game.mk_x = max(MK_W // 2 + 5, game.mk_x - MK_SPEED)
            elif key == ord("d") or key == 83:
                game.mk_x = min(W - MK_W // 2 - 5, game.mk_x + MK_SPEED)
            game.update()
        else:
            if key == ord("r"):
                game.reset()

        game.draw(canvas)
        # tampilkan nama lagu di pojok kanan bawah
        if nama_lagu:
            cv2.putText(canvas, f"musik: {nama_lagu}", (W - 250, H - 12),
                        FONT, 0.32, (120, 120, 120), 1)

        cv2.imshow("Math Bowl", canvas)

    if MUSIK:
        pygame.mixer.music.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
