import cv2
import numpy as np
import os

# ─────────────────────────────────────────────────────────────────────────────
#  project.py  —  Hand Detection Module
#  Metode: YCrCb skin segmentation + Face cascade exclusion
# ─────────────────────────────────────────────────────────────────────────────

# ── Face cascade ──────────────────────────────────────────────────────────────
_CASCADE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_ref.xml")
_face_cascade  = cv2.CascadeClassifier(_CASCADE_PATH)

# ── YCrCb skin range (standard Chai & Ngan) ───────────────────────────────────
# Lebih stabil terhadap perubahan cahaya dibanding HSV
_ycrcb_lower = np.array([0,   133, 77],  dtype=np.uint8)
_ycrcb_upper = np.array([255, 173, 127], dtype=np.uint8)

# ── Contour constraints ───────────────────────────────────────────────────────
_MIN_AREA     = 5000    # buang noise kecil
_MAX_AREA     = 60000   # buang objek terlalu besar (badan/background)
_MIN_SOLIDITY = 0.50    # tangan = solid; noise background = tidak solid

# ── Smoothing ─────────────────────────────────────────────────────────────────
_SMOOTH = 0.40

# ── Internal state ────────────────────────────────────────────────────────────
_sx: float | None = None
_sy: float | None = None


# ─────────────────────────────────────────────────────────────────────────────

def calibrate_from_roi(frame: np.ndarray, cx: int, cy: int, size: int = 30) -> None:
    """
    Kalibrasi warna kulit dari area kecil di sekitar (cx, cy).
    Panggil ini saat pengguna menaruh tangannya di titik tertentu.
    """
    global _ycrcb_lower, _ycrcb_upper
    h, w = frame.shape[:2]
    x1, y1 = max(0, cx - size), max(0, cy - size)
    x2, y2 = min(w, cx + size), min(h, cy + size)
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return
    ycrcb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb)
    cr    = ycrcb[:, :, 1].flatten()
    cb    = ycrcb[:, :, 2].flatten()
    tol   = 22                        # toleransi ±22 di setiap channel
    _ycrcb_lower = np.array([0,   max(0,   int(cr.mean()) - tol), max(0,   int(cb.mean()) - tol)], np.uint8)
    _ycrcb_upper = np.array([255, min(255, int(cr.mean()) + tol), min(255, int(cb.mean()) + tol)], np.uint8)
    print(f"[Calibration] Cr: {_ycrcb_lower[1]}–{_ycrcb_upper[1]}  "
          f"Cb: {_ycrcb_lower[2]}–{_ycrcb_upper[2]}")


def _make_skin_mask(frame: np.ndarray) -> np.ndarray:
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    return cv2.inRange(ycrcb, _ycrcb_lower, _ycrcb_upper)


def _exclude_faces(mask: np.ndarray, gray: np.ndarray) -> np.ndarray:
    """Zero-kan area wajah pada mask menggunakan Haar cascade."""
    if _face_cascade.empty():
        return mask
    faces = _face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
    )
    if len(faces) == 0:
        return mask
    result = mask.copy()
    h_frame = mask.shape[0]
    for (fx, fy, fw, fh) in faces:
        # Perluas ke bawah (leher + bahu atas)
        pad = int(fh * 0.6)
        y1  = max(0, fy)
        y2  = min(h_frame, fy + fh + pad)
        result[y1:y2, fx: fx + fw] = 0
    return result


def _clean(mask: np.ndarray) -> np.ndarray:
    # Blur ringan untuk hilangkan pixel terpisah
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    _, mask = cv2.threshold(mask, 80, 255, cv2.THRESH_BINARY)
    # Erosi → buang noise, Dilasi → rapatkan area utama
    k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    k7 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    mask = cv2.erode(mask,  k3, iterations=2)
    mask = cv2.dilate(mask, k7, iterations=3)
    return mask


def _good_contour(cnt) -> bool:
    area = cv2.contourArea(cnt)
    if not (_MIN_AREA <= area <= _MAX_AREA):
        return False
    hull_area = cv2.contourArea(cv2.convexHull(cnt))
    if hull_area == 0:
        return False
    return (area / hull_area) >= _MIN_SOLIDITY


def detect_hand(frame: np.ndarray) -> dict:
    """
    Deteksi tangan. Mengembalikan dict:
      hand_detected, hand_x, hand_y, palm_radius, bbox, mask
    """
    global _sx, _sy
    out = dict(hand_detected=False, hand_x=0, hand_y=0,
               palm_radius=0, bbox=None, mask=None)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 1. Skin mask (YCrCb)
    mask = _make_skin_mask(frame)

    # 2. Hapus area wajah
    mask = _exclude_faces(mask, gray)

    # 3. Bersihkan
    mask = _clean(mask)
    out["mask"] = mask

    # 4. Cari contour
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid   = [c for c in cnts if _good_contour(c)]
    if not valid:
        _sx = _sy = None
        return out

    # 5. Kontur terbesar yang valid
    best     = max(valid, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(best)

    # 6. Distance transform → temukan telapak (titik paling dalam kontur)
    cm = np.zeros(mask.shape, dtype=np.uint8)
    cv2.drawContours(cm, [best], -1, 255, cv2.FILLED)
    dist = cv2.distanceTransform(cm, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    _, palm_d, _, palm_pt = cv2.minMaxLoc(dist)
    cx, cy  = int(palm_pt[0]), int(palm_pt[1])
    palm_r  = max(1, int(palm_d))

    # 7. Smoothing
    if _sx is None:
        _sx, _sy = float(cx), float(cy)
    else:
        _sx = _sx * _SMOOTH + cx * (1 - _SMOOTH)
        _sy = _sy * _SMOOTH + cy * (1 - _SMOOTH)

    out.update(hand_detected=True,
               hand_x=int(_sx), hand_y=int(_sy),
               palm_radius=palm_r, bbox=(x, y, w, h))
    return out


def draw_detection(frame: np.ndarray, det: dict) -> np.ndarray:
    if not det["hand_detected"]:
        cv2.putText(frame, "Tangan tidak terdeteksi",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame
    x, y, w, h = det["bbox"]
    cx, cy, pr  = det["hand_x"], det["hand_y"], det["palm_radius"]
    cv2.rectangle(frame, (x, y), (x+w, y+h), (140, 140, 140), 1)
    cv2.circle(frame, (cx, cy), pr,  (255, 80, 0), 2)
    cv2.circle(frame, (cx, cy), 6,   (0, 0, 255), -1)
    cv2.circle(frame, (cx, cy), 6,   (255, 255, 255), 1)
    cv2.putText(frame, f"({cx},{cy})", (x, max(y-6, 14)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 140, 0), 1)
    return frame


# ── Standalone demo ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Hand Detection Demo")
    print("  C = kalibrasi (taruh tangan di tengah layar, tekan C)")
    print("  D = toggle mask debug | Q = keluar")

    cam = None
    for i in [0, 1, 2]:
        for b in [cv2.CAP_DSHOW, 0]:
            c = cv2.VideoCapture(i, b) if b else cv2.VideoCapture(i)
            if c.isOpened():
                ok, _ = c.read()
                if ok:
                    cam = c
                    break
                c.release()
        if cam:
            break
    if cam is None:
        print("Kamera tidak ditemukan"); exit(1)

    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    show_mask = True
    cv2.namedWindow("Hand Detection")

    while True:
        ok, frame = cam.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        det   = detect_hand(frame)
        vis   = draw_detection(frame.copy(), det)

        # Gambar crosshair kalibrasi di tengah
        h, w = frame.shape[:2]
        cv2.drawMarker(vis, (w//2, h//2), (0,255,0),
                       cv2.MARKER_CROSS, 40, 1)
        cv2.putText(vis, "Tekan C untuk kalibrasi",
                    (w//2 - 110, h//2 - 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow("Hand Detection", vis)
        if show_mask and det["mask"] is not None:
            cv2.imshow("Mask", det["mask"])

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            break
        elif key == ord("c"):
            calibrate_from_roi(frame, w//2, h//2, size=30)
        elif key == ord("d"):
            show_mask = not show_mask
            if not show_mask:
                cv2.destroyWindow("Mask")

    cam.release()
    cv2.destroyAllWindows()
