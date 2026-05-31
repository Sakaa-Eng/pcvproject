import cv2
import numpy as np
import os

CASCADE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_ref.xml")
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

skin_lower = np.array([0, 133, 77], dtype=np.uint8)
skin_upper = np.array([255, 173, 127], dtype=np.uint8)

MIN_AREA = 5000
MAX_AREA = 60000
MIN_SOLID = 0.50
SMOOTH = 0.40

sx = None
sy = None


def calibrate(frame, cx, cy, size=30):
    global skin_lower, skin_upper
    h, w = frame.shape[:2]
    x1 = max(0, cx - size)
    y1 = max(0, cy - size)
    x2 = min(w, cx + size)
    y2 = min(h, cy + size)
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return
    ycrcb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCrCb)
    cr = ycrcb[:, :, 1].flatten()
    cb = ycrcb[:, :, 2].flatten()
    tol = 22
    skin_lower = np.array([0, max(0, int(cr.mean()) - tol), max(0, int(cb.mean()) - tol)], np.uint8)
    skin_upper = np.array([255, min(255, int(cr.mean()) + tol), min(255, int(cb.mean()) + tol)], np.uint8)
    print(f"kalibrasi selesai: Cr {skin_lower[1]}-{skin_upper[1]}, Cb {skin_lower[2]}-{skin_upper[2]}")


def skin_mask(frame):
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    return cv2.inRange(ycrcb, skin_lower, skin_upper)


def remove_face(mask, gray):
    if face_cascade.empty():
        return mask
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
    if len(faces) == 0:
        return mask
    result = mask.copy()
    for (fx, fy, fw, fh) in faces:
        pad = int(fh * 0.6)
        result[fy:min(mask.shape[0], fy + fh + pad), fx:fx + fw] = 0
    return result


def clean_mask(mask):
    mask = cv2.GaussianBlur(mask, (5, 5), 0)
    _, mask = cv2.threshold(mask, 80, 255, cv2.THRESH_BINARY)
    k1 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    k2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    mask = cv2.erode(mask, k1, iterations=2)
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

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = skin_mask(frame)
    mask = remove_face(mask, gray)
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
    cx, cy = int(palm_pt[0]), int(palm_pt[1])
    palm_r = max(1, int(palm_d))

    if sx is None:
        sx, sy = float(cx), float(cy)
    else:
        sx = sx * SMOOTH + cx * (1 - SMOOTH)
        sy = sy * SMOOTH + cy * (1 - SMOOTH)

    result.update(hand_detected=True, hand_x=int(sx), hand_y=int(sy),
                  palm_radius=palm_r, bbox=(x, y, w, h))
    return result


def draw_detection(frame, det):
    if not det["hand_detected"]:
        cv2.putText(frame, "tangan tidak terdeteksi", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame
    x, y, w, h = det["bbox"]
    cx, cy, pr = det["hand_x"], det["hand_y"], det["palm_radius"]
    cv2.rectangle(frame, (x, y), (x + w, y + h), (140, 140, 140), 1)
    cv2.circle(frame, (cx, cy), pr, (255, 80, 0), 2)
    cv2.circle(frame, (cx, cy), 6, (0, 0, 255), -1)
    cv2.putText(frame, f"({cx},{cy})", (x, max(y - 6, 14)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 140, 0), 1)
    return frame


if __name__ == "__main__":
    cam = None
    for i in [0, 1, 2]:
        c = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if c.isOpened():
            ok, _ = c.read()
            if ok:
                cam = c
                break
            c.release()

    if cam is None:
        print("kamera tidak ditemukan")
        exit(1)

    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    show_mask = False
    cv2.namedWindow("Hand Detection")

    while True:
        ok, frame = cam.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        det = detect_hand(frame)
        vis = draw_detection(frame.copy(), det)

        fh, fw = frame.shape[:2]
        cv2.drawMarker(vis, (fw // 2, fh // 2), (0, 255, 0), cv2.MARKER_CROSS, 40, 1)

        cv2.imshow("Hand Detection", vis)
        if show_mask and det["mask"] is not None:
            cv2.imshow("Mask", det["mask"])

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            break
        elif key == ord("c"):
            calibrate(frame, fw // 2, fh // 2)
        elif key == ord("d"):
            show_mask = not show_mask
            if not show_mask:
                cv2.destroyWindow("Mask")

    cam.release()
    cv2.destroyAllWindows()
