import sys
import os
import time
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
import pyttsx3


# Configurations

IMAGE_ITEMS = [
    ("Food", "images/food.jpg"),
    ("Water", "images/bottle.jpg"),
    ("Restroom", "images/washroom.jpg"),
    ("Emergency", "images/emergency.jpg"),
    ("Outdoor", "images/outdoor.jpg"),
    ("Fan", "images/fan.png"),
    ("Apple", "images/apple.jpg"),
]

CASCADE_FACE = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
CASCADE_EYE = cv2.data.haarcascades + "haarcascade_eye.xml"

BLINK_MIN_CLOSED_TIME = 0.6
CYCLE_INTERVAL = 2.0


# TTS THREAD

class TTSWorker(QtCore.QThread):
    def __init__(self, text, engine):
        super().__init__()
        self.text = text
        self.engine = engine

    def run(self):
        try:
            self.engine.say(self.text)
            self.engine.runAndWait()
        except:
            pass


# MAIN WINDOW 

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Eye-Blink Communication")
        self.setGeometry(200, 200, 700, 550)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)

        self.text_label = QtWidgets.QLabel()
        self.text_label.setAlignment(QtCore.Qt.AlignCenter)
        self.text_label.setStyleSheet("font-size: 22px; font-weight: bold;")

        layout = QtWidgets.QVBoxLayout(central)
        layout.addWidget(self.image_label, stretch=3)
        layout.addWidget(self.text_label, stretch=1)

        self.items = IMAGE_ITEMS
        self.current_index = 0
        self.last_cycle_time = time.time()

        self.cap = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(CASCADE_FACE)
        self.eye_cascade = cv2.CascadeClassifier(CASCADE_EYE)

        self.closed_start_time = None
        self.blink_triggered = False

        # TTS
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        self.engine.setProperty('volume', 1.0)
        self.tts_thread = None

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(30)

        self.update_display()

    # GUI

    def update_display(self):
        label, path = self.items[self.current_index]
        self.text_label.setText(label)

        if not os.path.exists(path):
            self.image_label.setText(f"Missing image:\n{path}")
            return

        pixmap = QtGui.QPixmap(path)
        pixmap = pixmap.scaled(
            self.image_label.size(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )
        self.image_label.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()

    # CAMERA & BLINK 

    def process_frame(self):
        now = time.time()

        if now - self.last_cycle_time >= CYCLE_INTERVAL:
            self.current_index = (self.current_index + 1) % len(self.items)
            self.last_cycle_time = now
            self.update_display()

        ret, frame = self.cap.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        eyes_detected = False

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h // 2, x:x + w]

            eyes = self.eye_cascade.detectMultiScale(
                roi_gray,
                scaleFactor=1.1,
                minNeighbors=7,
                minSize=(30, 30)
            )

            if len(eyes) >= 1:
                eyes_detected = True

            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            break

        current_time = time.time()

        if not eyes_detected:
            if self.closed_start_time is None:
                self.closed_start_time = current_time

            elif (current_time - self.closed_start_time >= BLINK_MIN_CLOSED_TIME
                  and not self.blink_triggered):

                self.blink_triggered = True
                self.handle_long_blink()

        else:
            self.closed_start_time = None
            self.blink_triggered = False

        status = "Eyes Open" if eyes_detected else "Eyes Closed"
        cv2.putText(frame, status, (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Eye Tracking", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            self.close()

    # BLINK ACTION 

    def handle_long_blink(self):
        label, _ = self.items[self.current_index]
        print("Selected:", label)

        if self.tts_thread and self.tts_thread.isRunning():
            self.engine.stop()
            self.tts_thread.quit()
            self.tts_thread.wait()

        self.tts_thread = TTSWorker(label, self.engine)
        self.tts_thread.start()

        self.last_cycle_time = time.time()

    # CLEANUP 

    def closeEvent(self, event):
        self.cap.release()
        cv2.destroyAllWindows()
        super().closeEvent(event)


# RUN APP 

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()