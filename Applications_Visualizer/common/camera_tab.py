from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QImage, QPixmap
import cv2
import sys

from ultralytics import YOLO

class CameraTab(QWidget):
    def __init__ (self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.image_label = QLabel("Camera feed")

        self.display_height = 900
        self.display_width = 1500

        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black; font-size: 24px")
        self.image_label.setFixedSize(self.display_width, self.display_height)
        self.layout.addWidget(self.image_label)
        self.setLayout(self.layout) 

        self.capture = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.yolo_model = YOLO('yolov8n.pt')

        self.latest_radar_data = None

    
    def receive_radar_data(self, outputDict):
        self.latest_radar_data = outputDict


    def start_camera(self):
        # Check version to see if we need to use DSHOW (Alina this is what was causing the crash as well as needing the headless version)
        if self.capture is None:
            if sys.platform == "win32":
                self.capture = cv2.VideoCapture(1, cv2.CAP_DSHOW)

            else :
                self.capture = cv2.VideoCapture(1)

            self.timer.start(30)


    def stop_camera(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None
            self.timer.stop()


    def showEvent(self, event):
        self.start_camera()
        super().showEvent(event)

    def hideEvent(self, event):
        self.stop_camera()
        super().hideEvent(event)
    
    def closeEvent(self, event):
        self.stop_camera()
        super().closeEvent(event)


    def update_frame(self):
        if self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                frame = cv2.resize(frame, (self.display_width, self.display_height))
                h, w, ch = frame.shape

                results = self.yolo_model(frame, classes=[0], verbose=False)

                cv_boxes = [] 
                for box in results[0].boxes:
                    x1, y1, x2, y2 = map(int,box.xyxy[0])
                    cv_boxes.append((x1,y1,x2,y2))

                bytes_per_line = ch * w

                q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

                pixmap = QPixmap.fromImage(q_image)

                self.image_label.setPixmap(pixmap)
            else:
                self.image_label.setText("ITS NOT WORKING")
        else:
            self.image_label.setText("ITS NOT WORKING")

    

        