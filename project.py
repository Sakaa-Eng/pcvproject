import cv2
import numpy as np
import os

# deteksi objek biru (sarung tangan biru) pakai HSV
# range biru di HSV OpenCV (H: 0-179, S: 0-255, V: 0-255)
blue_lower = np.array([95, 60, 40],  dtype=np.uint8)
blue_upper = np.array([135, 255, 255], dtype=np.uint8)

MIN_AREA  = 3000
MAX_AREA  = 80000
MIN_SOLID = 0.35
SMOOTH    = 0.40

sx = None
sy = None


def calibrate(frame, cx, cy, size=30):
    """Kalibrasi range biru dari area kecil di sekitar (cx, cy)."""
    global blue_lower, blue_upper
    h, w = frame.shape[:2]
    x1 = max(0, cx - size)
    y1 = max(0, cy - size)
    x2 = min(w, cx + size)
    y2 = min(h, cy + size)
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    h_ch = hsv[:, :, 0].flatten()
    s_ch = hsv[:, :, 1].flatten()
    v_ch = hsv[:, :, 2].flatten()
    tol_h = 15
    tol_s = 60
    blue_lower = np.array([
        max(0,   int(h_ch.mean()) - tol_h),
        max(0,   int(s_ch.mean()) - tol_s),
        30
    ], np.uint8)
    blue_upper = np.array([
        min(179, int(h_ch.mean()) + tol_h),
        255,
        255
    ], np.uint8)
    print(f"kalibrasi biru: H {blue_lower[0]}-{blue_upper[0]}, S {blue_lower[1]}-{blue_upper[1]}")


def blue_mask(frame):
    """Buat mask untuk warna biru dari frame."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, blue_lower, blue_upper)


def clean_mask(mask):
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    _, mask = cv2.threshold(mask, 80, 255, cv2.THRESH_BINARY)
    k1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    k2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    mask = cv2.erode(mask, k1, iterations=1)
    mask = cv2.dilate(mask, k2, iterations=3)
    return mask


def valid_contour(cnt):
    area = cv2.contourArea(cnt)
    if not (MIN_AREA <= area <= MAX_AREA):
        return False
    hull_area = cv2.contourArea(cv2.convexHull(cnt))
    if hull_area == 0:
        return False
    return (area / hull_area) >= MIN_SOLID


def detect_hand(frame):
    global sx, sy
    result = {"hand_detected": False, "hand_x": 0, "hand_y": 0,
              "palm_radius": 0, "bbox": None, "mask": None}

    mask = blue_mask(frame)
    mask = clean_mask(mask)
    result["mask"] = mask

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid = [c for c in contours if valid_contour(c)]
    if not valid:
        sx = sy = None
        return result

    best = max(valid, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(best)

    cm = np.zeros(mask.shape, dtype=np.uint8)
    cv2.drawContours(cm, [best], -1, 255, cv2.FILLED)
    dist = cv2.distanceTransform(cm, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    _, palm_d, _, palm_pt = cv2.minMaxLoc(dist)
    cx_pt, cy_pt = int(palm_pt[0]), int(palm_pt[1])
    palm_r = max(1, int(palm_d))

    if sx is None:
        sx, sy = float(cx_pt), float(cy_pt)
    else:
        sx = sx * SMOOTH + cx_pt * (1 - SMOOTH)
        sy = sy * SMOOTH + cy_pt * (1 - SMOOTH)

    result.update(hand_detected=True, hand_x=int(sx), hand_y=int(sy),
                  palm_radius=palm_r, bbox=(x, y, w, h))
    return result


def draw_detection(frame, det):
    if not det["hand_detected"]:
        cv2.putText(frame, "sarung tangan biru tidak terdeteksi", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        return frame
    x, y, w, h = det["bbox"]
    cx, cy, pr = det["hand_x"], det["hand_y"], det["palm_radius"]
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.circle(frame, (cx, cy), pr, (255, 80, 0), 2)
    cv2.circle(frame, (cx, cy), 6, (0, 0, 255), -1)
    cv2.putText(frame, f"({cx},{cy})", (x, max(y - 6, 14)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
    return frame


if __name__ == "__main__":
    print("Deteksi Sarung Tangan Biru")
    print("c = kalibrasi (taruh sarung tangan di tengah, tekan c)")
    print("d = toggle mask  |  q = keluar")

    backends = [cv2.CAP_MSMF, cv2.CAP_DSHOW, 0]
    cam = None
    for i in [0, 1, 2]:
        for backend in backends:
            try:
                c = cv2.VideoCapture(i, backend) if backend != 0 else cv2.VideoCapture(i)
                if c.isOpened():
                    ok, _ = c.read()
                    if ok:
                        cam = c
                        print(f"[kamera index {i} aktif]")
                        break
                    c.release()
            except:
                continue
        if cam:
            break

    if cam is None:
        print("kamera tidak ditemukan")
        exit(1)

    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    show_mask = False
    cv2.namedWindow("Deteksi Sarung Tangan Biru")

    while True:
        ok, frame = cam.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        det = detect_hand(frame)
        vis = draw_detection(frame.copy(), det)

        fh, fw = frame.shape[:2]
        cv2.drawMarker(vis, (fw // 2, fh // 2), (0, 255, 0), cv2.MARKER_CROSS, 40, 1)
        cv2.putText(vis, "c=kalibrasi  d=mask  q=keluar",
                    (8, fh - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (80, 80, 80), 1)

        cv2.imshow("Deteksi Sarung Tangan Biru", vis)
        if show_mask and det["mask"] is not None:
            cv2.imshow("Mask Biru", det["mask"])

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            break
        elif key == ord("c"):
            calibrate(frame, fw // 2, fh // 2)
        elif key == ord("d"):
            show_mask = not show_mask
            if not show_mask:
                cv2.destroyWindow("Mask Biru")

    cam.release()
    cv2.destroyAllWindows()
