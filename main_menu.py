import cv2
import numpy as np

from game import main as jalankan_game1
from game_mode2 import main as jalankan_game2

W, H = 640, 480
FONT = cv2.FONT_HERSHEY_SIMPLEX


def gambar_tombol(canvas, x1, y1, x2, y2, teks, aktif):
    warna = (80, 80, 160) if aktif else (150, 150, 150)
    cv2.rectangle(canvas, (x1, y1), (x2, y2), warna, -1)
    cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 0, 0), 2)
    (tw, th), _ = cv2.getTextSize(teks, FONT, 0.8, 2)
    tx = x1 + (x2 - x1 - tw) // 2
    ty = y1 + (y2 - y1 + th) // 2
    cv2.putText(canvas, teks, (tx, ty), FONT, 0.8, (255, 255, 255), 2)


def layar_menu(canvas, pilihan):
    canvas[:] = 210

    # judul
    cv2.putText(canvas, "Math Bowl", (W // 2 - 140, 130), FONT, 2.0, (0, 0, 0), 3)
    cv2.line(canvas, (150, 150), (490, 150), (100, 100, 100), 2)

    # tombol START
    gambar_tombol(canvas, 210, 210, 430, 265, "START", pilihan == 0)

    # tombol QUIT
    gambar_tombol(canvas, 210, 295, 430, 350, "QUIT", pilihan == 1)

    cv2.putText(canvas, "w/s = pilih   enter = konfirmasi",
                (145, 430), FONT, 0.42, (80, 80, 80), 1)


def layar_pilih_mode(canvas, pilihan):
    canvas[:] = 210

    cv2.putText(canvas, "Pilih Mode", (W // 2 - 105, 120), FONT, 1.4, (0, 0, 0), 2)
    cv2.line(canvas, (150, 140), (490, 140), (100, 100, 100), 2)

    # mode 1
    gambar_tombol(canvas, 80, 190, 560, 255, "Tebak Jawaban", pilihan == 0)
    cv2.putText(canvas, "tangkap bola dengan jawaban yang benar",
                (105, 275), FONT, 0.42, (60, 60, 60), 1)

    # mode 2
    gambar_tombol(canvas, 80, 300, 560, 365, "Tebak Operasi Matematika", pilihan == 1)
    cv2.putText(canvas, "gerakkan tangan, susun angka dan operator",
                (105, 385), FONT, 0.42, (60, 60, 60), 1)

    cv2.putText(canvas, "w/s = pilih   enter = pilih   esc = kembali",
                (115, 440), FONT, 0.42, (80, 80, 80), 1)


def main():
    cv2.namedWindow("Math Bowl")
    canvas = np.ones((H, W, 3), dtype=np.uint8) * 210

    state   = "menu"   # "menu" atau "mode"
    pilihan = 0

    while True:
        key = cv2.waitKey(30) & 0xFF

        if state == "menu":
            layar_menu(canvas, pilihan)

            if key == ord("w") or key == 82:
                pilihan = (pilihan - 1) % 2
            elif key == ord("s") or key == 84:
                pilihan = (pilihan + 1) % 2
            elif key == 13 or key == ord(" "):   # enter atau spasi
                if pilihan == 0:
                    state   = "mode"
                    pilihan = 0
                else:
                    break
            elif key == ord("q") or key == 27:
                break

        elif state == "mode":
            layar_pilih_mode(canvas, pilihan)

            if key == ord("w") or key == 82:
                pilihan = (pilihan - 1) % 2
            elif key == ord("s") or key == 84:
                pilihan = (pilihan + 1) % 2
            elif key == 13 or key == ord(" "):
                cv2.destroyAllWindows()
                if pilihan == 0:
                    jalankan_game1()
                else:
                    jalankan_game2()
                cv2.namedWindow("Math Bowl")
                state   = "menu"
                pilihan = 0
            elif key == ord("1"):
                cv2.destroyAllWindows()
                jalankan_game1()
                cv2.namedWindow("Math Bowl")
                state   = "menu"
                pilihan = 0
            elif key == ord("2"):
                cv2.destroyAllWindows()
                jalankan_game2()
                cv2.namedWindow("Math Bowl")
                state   = "menu"
                pilihan = 0
            elif key == 27:   # esc = kembali ke menu
                state   = "menu"
                pilihan = 0

        cv2.imshow("Math Bowl", canvas)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
