import sys
import os


# Ensure Applications_Visualizer and common are on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COMMON = os.path.join(ROOT, "common")

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

if COMMON not in sys.path:
    sys.path.insert(0, COMMON)


def test_import_gui_main():
    # Sanity check that gui_main imports without crashing.
    import gui_main
    assert gui_main is not None


def test_qt_application_initializes():
    # Ensure Qt can initialize.
    from PySide2.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    assert app is not None
