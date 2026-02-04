from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QImage, QPixmap
import cv2

class CameraTab(QWidget):
    def __init__ (self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.image_label = QLabel("Camera feed")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black; font-size: 24px")
        self.layout.addWidget(self.image_label)
        self.setLayout(self.layout) 

        self.capture = cv2.VideoCapture(0,cv2.CAP_DSHOW)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        if self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


                h, w, ch = frame.shape

                bytes_per_line = ch * w

                q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

                pixmap = QPixmap.fromImage(q_image)
                scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio)

                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText("ITS NOT WORKING")
        else:
            self.image_label.setText("ITS NOT WORKING")

    
    def stop_camera(self):
        if self.capture.isOpened():
            self.capture.release()
            self.timer.stop()

    def closeEvent(self, event):
        self.stop_camera()
        super().closeEvent(event)
        