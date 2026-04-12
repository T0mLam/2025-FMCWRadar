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

# ─────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# Window Tests
# ─────────────────────────────────────────────
def test_import_gui_main():
    # Sanity check that gui_main imports without crashing.
    import gui_main
    assert gui_main is not None

def test_window_title(window):
    """Verify the window has the correct default title."""
    assert window.windowTitle() == "Applications Visualizer"


def test_window_is_visible(window):
    """Verify the window is visible after initialization."""
    assert window.isVisible()

# ─────────────────────────────────────────────
# Connection Pane Tests
# ─────────────────────────────────────────────
def test_connection_pane_exists(window):
    """Verify that the connection group box exists."""
    assert window.comBox is not None
    assert isinstance(window.comBox, QGroupBox)
    assert window.comBox.title() == "Connect to COM Ports"

def test_connect_button_exists(window):
    """Verify that the connect button exists and has the correct text."""
    assert window.connectButton is not None
    assert isinstance(window.connectButton, QPushButton)
    assert window.connectButton.text() == "Connect"

def test_connect_status_default(window):
    """Verify default connection status is 'Not Connected'."""
    assert window.connectStatus.text() == "Not Connected"

def test_devide_list_exists(window):
    """Verify the device dropdown exists and has items."""
    assert window.deviceList is not None
    assert isinstance(window.deviceList, QComboBox)
    assert window.deviceList.count() > 0

def test_demo_list_exists(window):
    """Verify the demo dropdown exists and has items."""
    assert window.demoList is not None
    assert isinstance(window.demoList, QComboBox)
    assert window.demoList.count() > 0

# ─────────────────────────────────────────────
# Recording Pane Tests
# ─────────────────────────────────────────────
