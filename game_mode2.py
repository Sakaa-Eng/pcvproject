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

TANGAN_SPEED = 6
RADIUS_BOLA  = 22
NYAWA        = 3
POIN         = 10


# ── musik ──────────────────────────────────────────────────
def cari_lagu(folder="music"):
    if not MUSIK:
        return None
    if not os.path.exists(folder):
        return None
    ext = ('.mp3', '.wav', '.ogg')
    files = [f for f in os.listdir(folder) if f.lower().endswith(ext)]
    if not files:
        return None
    return os.path.join(folder, random.choice(files))

def putar_musik(path):
    if not MUSIK or path is None:
        return
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        print(f"memutar: {os.path.basename(path)}")
    except Exception as e:
        print(f"gagal putar musik: {e}")


# ── helper gambar tangan merah ──────────────────────────────
def gambar_tangan(canvas, x, y):
    # telapak
    palm = np.array([
        [x - 14, y + 5],
        [x + 14, y + 5],
        [x + 14, y - 8],
        [x - 14, y - 8],
    ], np.int32)
    cv2.fillPoly(canvas, [palm], (0, 0, 200))

    # 5 jari
    offsets = [-10, -5, 0, 5, 10]
    heights = [22, 28, 26, 22, 16]
    for ox, h in zip(offsets, heights):
        pts = np.array([
            [x + ox - 4, y - 8],
            [x + ox + 4, y - 8],
            [x + ox,     y - 8 - h],
        ], np.int32)
        cv2.fillPoly(canvas, [pts], (0, 0, 200))

    # outline telapak
    cv2.polylines(canvas, [palm], True, (0, 0, 130), 1)


# ── class bola ─────────────────────────────────────────────
class Bola:
    def __init__(self, x, y, label):
        self.x       = x
        self.y       = y
        self.label   = label   # bisa angka string atau '+' '-' 'x'
        self.dipilih = False
        self.urutan  = -1


# ── buat soal ──────────────────────────────────────────────
def buat_soal():
    op = random.choice(['+', '-'])
    a  = random.randint(1, 9)
    b  = random.randint(1, 9)
    target = a + b if op == '+' else a - b
    return target, a, op, b


def buat_bola(target, a, op, b):
    # label yang harus ada: angka a, operator, angka b
    labels = [str(a), op, str(b)]

    # distraktor angka
    dist = set()
    while len(dist) < 3:
        d = random.randint(1, 9)
        if d != a and d != b:
            dist.add(d)
    for d in dist:
        labels.append(str(d))

    # distraktor operator
    op_lain = [o for o in ['+', '-'] if o != op]
    labels.append(random.choice(op_lain))

    random.shuffle(labels)

    # tempatkan di grid agar tidak dempet
    cols, rows = 4, 2
    cell_w = (W - 80) // cols
    cell_h = (H - 160) // rows
    cells  = [(c, r) for r in range(rows) for c in range(cols)]
    random.shuffle(cells)

    bola_list = []
    for i, label in enumerate(labels):
        if i >= len(cells):
            break
        c, r = cells[i]
        x = 50 + c * cell_w + random.randint(10, max(10, cell_w - RADIUS_BOLA * 2 - 10))
        y = 80 + r * cell_h + random.randint(10, max(10, cell_h - RADIUS_BOLA * 2 - 10))
        bola_list.append(Bola(x, y, label))

    return bola_list


# ── class game ─────────────────────────────────────────────
class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.skor       = 0
        self.nyawa      = NYAWA
        self.over       = False
        self.tangan_x   = W // 2
        self.tangan_y   = H // 2
        self.ekspresi   = []     # label yang sudah dipilih
        self.pesan      = ""
        self.pesan_t    = 0
        self.soal_baru()

    def soal_baru(self):
        self.target, a, op, b = buat_soal()
        self.bola_list = buat_bola(self.target, a, op, b)
        self.ekspresi  = []

    def reset_pilihan(self):
        self.ekspresi = []
        for bola in self.bola_list:
            bola.dipilih = False
            bola.urutan  = -1

    def update(self):
        if self.over:
            return

        # cek tangan menyentuh bola
        for bola in self.bola_list:
            if bola.dipilih:
                continue
            dist = ((self.tangan_x - bola.x) ** 2 + (self.tangan_y - bola.y) ** 2) ** 0.5
            if dist < RADIUS_BOLA + 12:
                bola.dipilih = True
                bola.urutan  = len(self.ekspresi)
                self.ekspresi.append(bola.label)
                self._cek()
                break

        if self.pesan_t > 0:
            self.pesan_t -= 1

    def _cek(self):
        e = self.ekspresi
        # cari pola angka-operator-angka di ekspresi
        for i in range(len(e) - 2):
            try:
                a   = int(e[i])
                op  = e[i + 1]
                b   = int(e[i + 2])
                if op == '+':
                    hasil = a + b
                elif op == '-':
                    hasil = a - b
                elif op == 'x':
                    hasil = a * b
                else:
                    continue

                if hasil == self.target:
                    self.skor += POIN
                    self.pesan   = "bonus mbg 100"
                    self.pesan_t = 50
                    self.soal_baru()
                    return
            except:
                continue

        # kalau ekspresi sudah 5 item dan belum ada yang benar → salah
        if len(e) >= 5:
            self.nyawa  -= 1
            self.pesan   = "Salah! coba lagi"
            self.pesan_t = 40
            if self.nyawa <= 0:
                self.over = True
            else:
                self.reset_pilihan()

    def draw(self, canvas):
        canvas[:] = 220

        # header
        cv2.rectangle(canvas, (0, 0), (W, 55), (160, 160, 160), -1)
        cv2.putText(canvas, f"Nilai berapa yg hasilnya {self.target}?",
                    (10, 36), FONT, 0.8, (0, 0, 0), 2)

        # skor & nyawa
        cv2.putText(canvas, f"Skor: {self.skor}", (W - 130, 24), FONT, 0.55, (0, 0, 0), 1)
        for i in range(self.nyawa):
            cv2.rectangle(canvas, (W - 25 - i * 28, 32), (W - 8 - i * 28, 48), (0, 0, 200), -1)

        # gambar bola
        for bola in self.bola_list:
            bx, by = bola.x, bola.y
            warna  = (140, 140, 140) if bola.dipilih else (60, 60, 180)
            cv2.circle(canvas, (bx, by), RADIUS_BOLA, warna, -1)
            cv2.circle(canvas, (bx, by), RADIUS_BOLA, (0, 0, 0), 2)

            (tw, th), _ = cv2.getTextSize(bola.label, FONT, 0.9, 2)
            cv2.putText(canvas, bola.label,
                        (bx - tw // 2, by + th // 2),
                        FONT, 0.9, (255, 255, 255), 2)

            # nomor urut pilihan
            if bola.dipilih:
                cv2.putText(canvas, str(bola.urutan + 1),
                            (bx + RADIUS_BOLA - 8, by - RADIUS_BOLA + 12),
                            FONT, 0.45, (0, 0, 0), 1)

        # gambar tangan
        gambar_tangan(canvas, self.tangan_x, self.tangan_y)

        # ekspresi saat ini
        expr_str = " ".join(self.ekspresi) if self.ekspresi else "-"
        cv2.putText(canvas, f"Pilihanmu: {expr_str}",
                    (10, H - 30), FONT, 0.5, (30, 30, 30), 1)

        # pesan benar/salah
        if self.pesan_t > 0:
            warna_p = (0, 130, 0) if "Benar" in self.pesan else (0, 0, 200)
            cv2.putText(canvas, self.pesan,
                        (W // 2 - 120, H // 2),
                        FONT, 0.75, warna_p, 2)

        # instruksi
        cv2.putText(canvas, "wasd/arrow=gerak  r=reset pilihan  q=keluar",
                    (8, H - 12), FONT, 0.36, (90, 90, 90), 1)

        # game over
        if self.over:
            cv2.rectangle(canvas, (100, 150), (W - 100, 330), (50, 50, 50), -1)
            cv2.rectangle(canvas, (100, 150), (W - 100, 330), (0, 0, 0), 2)
            cv2.putText(canvas, "GAME OVER", (155, 225), FONT, 1.4, (0, 0, 255), 3)
            cv2.putText(canvas, f"Skor: {self.skor}", (210, 270), FONT, 0.8, (255, 255, 255), 2)
            cv2.putText(canvas, "tekan R untuk main lagi", (152, 310), FONT, 0.52, (200, 200, 200), 1)


# ── main ───────────────────────────────────────────────────
def buka_kamera():
    backends = [cv2.CAP_MSMF, cv2.CAP_DSHOW, 0]
    for i in [0, 1, 2]:
        for backend in backends:
            try:
                c = cv2.VideoCapture(i, backend) if backend != 0 else cv2.VideoCapture(i)
                if c.isOpened():
                    ok, _ = c.read()
                    if ok:
                        c.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        c.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        print(f"[kamera index {i} aktif]")
                        return c
                c.release()
            except:
                continue
    print("[kamera tidak ditemukan, pakai keyboard]")
    return None


def main():
    from project import detect_hand

    lagu = cari_lagu("music")
    putar_musik(lagu)
    nama_lagu = os.path.basename(lagu) if lagu else ""

    cam = buka_kamera()

    cv2.namedWindow("Math Bowl - Mode Susun")
    canvas = np.ones((H, W, 3), dtype=np.uint8) * 220
    game   = Game()

    frame    = None
    hand_det = False

    while True:
        key = cv2.waitKey(30) & 0xFF

        # baca kamera dan deteksi tangan
        if cam:
            ret, frame = cam.read()
            if ret:
                frame    = cv2.flip(frame, 1)
                det      = detect_hand(frame)
                hand_det = det["hand_detected"]
                if hand_det and not game.over:
                    # kursor tangan mengikuti posisi tangan di kamera
                    tx = det["hand_x"]
                    ty = det["hand_y"]
                    tx = max(20, min(W - 20, tx))
                    ty = max(20, min(H - 20, ty))
                    game.tangan_x += int((tx - game.tangan_x) * 0.5)
                    game.tangan_y += int((ty - game.tangan_y) * 0.5)

        if key == ord("q") or key == 27:
            break

        if not game.over:
            # keyboard fallback kalau tangan tidak terdeteksi
            if not hand_det:
                if key == ord("w") or key == 82:
                    game.tangan_y = max(20, game.tangan_y - TANGAN_SPEED)
                elif key == ord("s") or key == 84:
                    game.tangan_y = min(H - 20, game.tangan_y + TANGAN_SPEED)
                elif key == ord("a") or key == 81:
                    game.tangan_x = max(20, game.tangan_x - TANGAN_SPEED)
                elif key == ord("d") or key == 83:
                    game.tangan_x = min(W - 20, game.tangan_x + TANGAN_SPEED)
            if key == ord("r"):
                game.reset_pilihan()
            game.update()
        else:
            if key == ord("r"):
                game.reset()

        game.draw(canvas)

        # preview kamera kecil di pojok kanan bawah
        if cam and frame is not None:
            prev = cv2.resize(frame, (160, 120))
            if hand_det and det["bbox"]:
                bx, by, bw, bh = det["bbox"]
                cv2.rectangle(prev,
                    (int(bx * 160 / 640), int(by * 120 / 480)),
                    (int((bx + bw) * 160 / 640), int((by + bh) * 120 / 480)),
                    (0, 255, 0), 1)
            canvas[H - 120:H, W - 160:W] = prev
            status  = "tangan OK" if hand_det else "tangan -"
            warna_s = (0, 180, 0) if hand_det else (0, 0, 200)
            cv2.putText(canvas, status, (W - 158, H - 123), FONT, 0.35, warna_s, 1)


        if nama_lagu:
            cv2.putText(canvas, f"musik: {nama_lagu}", (8, H - 12),
                        FONT, 0.32, (120, 120, 120), 1)

        cv2.imshow("Math Bowl - Mode Susun", canvas)

    if cam:
        cam.release()
    if MUSIK:
        pygame.mixer.music.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
