import sys
import os
import pytest


# Ensure Applications_Visualizer and common are on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COMMON = os.path.join(ROOT, "common")

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

if COMMON not in sys.path:
    sys.path.insert(0, COMMON)

from PySide2.QtWidgets import (
    QApplication, QPushButton, QLabel, QLineEdit, QComboBox, QRadioButton, QGroupBox, QSlider
)
from PySide2.QtTest import QTest
from PySide2.QtCore import Qt

#--------------------------------------------------------
# FIXTURES
#--------------------------------------------------------
@pytest.fixture(scope="session")
def app():
    application = QApplication.instance()
    if application is None:
        application = QApplication(sys.argv)
    yield application

@pytest.fixture
def window(app):
    from gui_main import Window
    win = Window()
    yield win
    win.close()

#--------------------------------------------------------
# Window Tests
#--------------------------------------------------------
def test_import_gui_main():
    # Sanity check that gui_main imports without crashing.
    import gui_main
    assert gui_main is not None

