import cv2

face_ref = cv2.CascadeClassifier("face_ref.xml")

# SOLUSI 1: Tambahkan cv2.CAP_DSHOW untuk mengatasi error backend dshow dan Camera index pada Windows
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

def face_detection(frame):
    optimized_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_ref.detectMultiScale(optimized_frame, scaleFactor=1.1)
    return faces

def drawer_box(frame):
    for x,y,w,h in face_detection(frame):
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    
def close_window():
    camera.release()
    cv2.destroyAllWindows()
    exit()
#testing pcv
def main (): 
    while True:
        # Ubah _ menjadi ret untuk menangkap status keberhasilan baca frame
        ret, frame = camera.read()
        
        # SOLUSI 2: Cek apakah frame berhasil dibaca. Jika tidak, hentikan program 
        # agar tidak diteruskan ke cvtColor dan memicu error !_src.empty()
        if not ret or frame is None:
            print("Gagal mengambil frame dari kamera. Pastikan kamera tidak sedang dipakai aplikasi lain.")
            break

        drawer_box(frame)
        cv2.imshow("Project", frame)
        cv2.waitKey(1)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            close_window()

if __name__ == "__main__":
    main()
 
print("OpenCV version:", cv2.__version__)