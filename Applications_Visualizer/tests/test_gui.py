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

def test_record_button_exists(window):
    """Verify the record data button exists."""
    assert window.dataRecordButton is not None
    assert isinstance(window.dataRecordButton, QPushButton)
    assert window.dataRecordButton.text() == "Record Data"

def test_duration_field_default(window):
    """Verify the duration field has default value of 3."""
    assert window.durationEdit is not None
    assert window.durationEdit.text() == "3"

def test_duration_field_accepts_input(window):
    """Verify user can type into the duration field."""
    window.durationEdit.clear()
    QTest.keyClicks(window.durationEdit, "10")
    assert window.durationEdit.text() == "10"

def test_data_file_base_default(window):
    """Verify the data file base name has a default value."""
    assert window.dataFileBaseEdit is not None
    assert window.dataFileBaseEdit.text() == "data"

def test_data_file_base_accepts_input(window):
    """Verify user can type a custom file name."""
    window.dataFileBaseEdit.clear()
    QTest.keyClicks(window.dataFileBaseEdit, "my_recording")
    assert window.dataFileBaseEdit.text() == "my_recording"

# ─────────────────────────────────────────────
# Configuration Pane Tests
# ─────────────────────────────────────────────

def test_config_pane_exists(window):
    """Verify the configuration group box exists."""
    assert window.configBox is not None
    assert isinstance(window.configBox, QGroupBox)
    assert window.configBox.title() == "Configuration"

def test_select_config_button_exists(window):
    """Verify the select configuration button exists."""
    assert window.selectConfig is not None
    assert window.selectConfig.text() == "Select Configuration"

def test_send_config_button_disabled_by_default(window):
    """Send config should be disabled until connected."""
    assert window.sendConfig.isEnabled() is False

def test_start_button_disabled_by_default(window):
    """Start button should be disabled until connected."""
    assert window.start.isEnabled() is False

def test_sensor_stop_hidden_by_default(window):
    """Sensor stop button should be hidden by default."""
    assert window.sensorStop.isHidden()

# ─────────────────────────────────────────────
# Mode Pane Tests
# ─────────────────────────────────────────────

def test_mode_pane_exists(window):
    """Verify the mode group box exists."""
    assert window.modeBox is not None
    assert isinstance(window.modeBox, QGroupBox)
    assert window.modeBox.title() == "Data/Model"

def test_radio_buttons_exist(window):
    """Verify both radio buttons exist."""
    assert window.radio_data_button is not None
    assert window.radio_gait_button is not None
    assert isinstance(window.radio_data_button, QRadioButton)
    assert isinstance(window.radio_gait_button, QRadioButton)

def test_data_mode_selected_by_default(window):
    """Verify 'Record Data' is the default selected mode."""
    assert window.radio_data_button.isChecked()
    assert not window.radio_gait_button.isChecked()

def test_switch_to_gait_mode(window):
    """Verify switching to gait recognition mode works."""
    window.radio_gait_button.setChecked(True)
    assert window.radio_gait_button.isChecked()
    assert not window.radio_data_button.isChecked()
    assert window.core.parser.enable_gait_model is True

def test_switch_back_to_data_mode(window):
    """Verify switching back to data mode works."""
    window.radio_gait_button.setChecked(True)
    window.radio_data_button.setChecked(True)
    assert window.radio_data_button.isChecked()
    assert window.core.parser.enable_gait_model is False

# ─────────────────────────────────────────────
# Menu Bar Tests
# ─────────────────────────────────────────────

def test_menu_bar_exists(window):
    """Verify the menu bar exists."""
    menu_bar = window.menuBar()
    assert menu_bar is not None

def test_help_menu_exists(window):
    """Verify the Help menu exists."""
    menu_bar = window.menuBar()
    actions = menu_bar.actions()
    menu_texts = [a.text() for a in actions]
    assert "&Help" in menu_texts

def test_help_action_exists(window):
    """Verify the user guide action exists."""
    assert window.helpAction is not None
    assert window.helpAction.text() == "Visualizer User Guide"

# ─────────────────────────────────────────────
# Replay Pane Tests
# ─────────────────────────────────────────────

def test_replay_box_hidden_by_default(window):
    """Verify the replay box is hidden by default."""
    assert window.replayBox.isVisible() is False

def test_slider_exists(window):
    """Verify the replay slider exists with correct range."""
    slider = window.core.sl
    assert slider is not None
    assert isinstance(slider, QSlider)
    assert slider.minimum() == 0
    assert slider.maximum() == 30
    assert slider.value() == 20