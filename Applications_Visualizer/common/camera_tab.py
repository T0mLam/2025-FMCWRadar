from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide2.QtCore import Qt

class CameraTab(QWidget):
    def __init__ (self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.image_label = QLabel("Camera feed")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black; font-size: 24px")
        self.layout.addWidget(self.image_label)
        self.setLayout(self.layout) 