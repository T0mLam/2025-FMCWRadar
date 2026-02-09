# General Library Imports
from serial.tools import list_ports
import os
import subprocess
import sys
from contextlib import suppress

# PyQt Imports
from PySide2 import QtGui
from PySide2.QtCore import QTimer, Qt, QUrl
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import (
    QAction,
    QTabWidget,
    QGridLayout,
    QMenu,
    QGroupBox,
    QLineEdit,
    QLabel,
    QPushButton,
    QComboBox,
    QRadioButton,
    QFileDialog,
    QMainWindow,
    QWidget,
    QShortcut,
    QSlider,
    QMessageBox,
    QApplication,
    QVBoxLayout,
)
from pathlib import Path

# Local Imports
from demo_defines import *
from gui_threads import *

from Demo_Classes.out_of_box_x432 import OOBx432

from camera_tab import CameraTab
# Logger
import logging
log = logging.getLogger(__name__)


class Window(QMainWindow):
    def __init__(self, parent=None, size=[], title="Applications Visualizer"):
        super(Window, self).__init__(parent)

        self.core = Core()
        self.setWindowIcon(QtGui.QIcon("./images/logo.png"))

        self.shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.shortcut.activated.connect(self.close)

        # Set the layout
        # Create tab for different graphing options
        self.demoTabs = QTabWidget()

        self.gridLayout = QGridLayout()

        # Add connect options
        self.initConfigPane()
        self.initConnectionPane()

        # MODE SWITCH PANE

        self.initModePane()

        #NICETOHAVE flag to prevent multiple config sends
        self.send_cfg = False
        self.send_cfg_first = False


        self.gridLayout.addWidget(self.comBox, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.configBox, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.demoTabs, 0, 1, 8, 1)

        # MODE SWITCH COORDS
        self.gridLayout.addWidget(self.modeBox,7,0,1,1)

        self.core.sl.setMinimum(0)
        self.core.sl.setMaximum(30)
        self.core.sl.setValue(20)
        self.core.sl.setTickPosition(QSlider.TicksBelow)
        self.core.sl.setTickInterval(5)

        self.replayBox = QGroupBox("Replay")
        self.replayLayout = QGridLayout()
        self.replayLayout.addWidget(self.core.sl, 0, 0, 1, 1)
        self.replayBox.setLayout(self.replayLayout)
        self.replayBox.setVisible(False)
        self.gridLayout.addWidget(self.replayBox, 8, 0, 1, 2)

        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 5)

        self.central = QWidget()
        self.central.setLayout(self.gridLayout)

        self.setWindowTitle(title)
        self.initMenuBar()
        self.core.replay = False

        self.setCentralWidget(self.central)

        self.showMaximized()

    def initMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        helpMenu = QMenu("&Help", self)

        self.helpAction = QAction("Visualizer User Guide", self)

        self.helpAction.triggered.connect(self.openUserGuide)
        helpMenu.addAction(self.helpAction)
        menuBar.addMenu(helpMenu)

    def openUserGuide(self):
        #TODO change when user instructions ready
        userGuideURL = QUrl('https://dev.ti.com/tirex/local?id=mmwave_applications_visualizer_user_guide&packageId=radar_toolbox')
        openUserGuide = QtGui.QDesktopServices.openUrl(userGuideURL)
        
        if not openUserGuide:
            QtGui.QMessageBox.warning(self, 'ERROR', 'Unable to open the Visualizer User Guide')
            log.error("Unable to open the Visualizer User Guide")
    
    def initConnectionPane(self):
        self.comBox = QGroupBox("Connect to COM Ports")
        self.cliCom = QLineEdit("")
        self.connectStatus = QLabel("Not Connected")
        self.connectButton = QPushButton("Connect")
        self.connectButton.clicked.connect(self.onConnect)
        self.demoList = QComboBox()
        self.deviceList = QComboBox()
        
         # Duration Label
        self.durationLabel = QLabel("Duration (s):")
        self.durationEdit = QLineEdit("3") # Default to 3 seconds
        self.durationEdit.setToolTip("Enter recording duration in seconds")
        self.dataFileBaseLabel = QLabel("Data file name:")
        self.dataFileBaseEdit = QLineEdit("data")   # default base name
        self.dataFileBaseEdit.setToolTip("Base name. File will save as <name>_<n>.json")

          # Record Push Button
        self.dataRecordButton = QPushButton("Record Data", self)
        self.dataRecordButton.clicked.connect(self.startDataRecording)

         # Timer
        self.mdTimer = QTimer(self) 
        self.mdTimer.setSingleShot(True)
        self.mdTimer.timeout.connect(self.stopDataRecording)

        self.demoList.addItems(self.core.getDemoList())
        self.demoList.currentIndexChanged.connect(self.onChangeDemo)
        self.deviceList.addItems(self.core.getDeviceList())
        self.deviceList.currentIndexChanged.connect(self.onChangeDevice)
        self.comLayout = QGridLayout()
        self.comLayout.addWidget(QLabel("Device:"), 0, 0)
        self.comLayout.addWidget(self.deviceList, 0, 1)
        self.comLayout.addWidget(QLabel("CLI COM:"), 1, 0)
        self.comLayout.addWidget(self.cliCom, 1, 1)
        self.comLayout.addWidget(QLabel("Demo:"), 2, 0)
        self.comLayout.addWidget(self.demoList, 2, 1)
    
       
        self.comLayout.addWidget(self.connectButton, 4, 0) 
        self.comLayout.addWidget(self.connectStatus, 4, 1)

        self.comLayout.addWidget(self.durationLabel, 6, 0)
        self.comLayout.addWidget(self.durationEdit, 6, 1)
        self.comLayout.addWidget(self.dataFileBaseLabel, 7, 0)
        self.comLayout.addWidget(self.dataFileBaseEdit, 7, 1)
        self.comLayout.addWidget(self.dataRecordButton, 8, 0, 1, 2)

        self.comBox.setLayout(self.comLayout)
        self.demoList.setCurrentIndex(0)  # initialize this to a stable value

        # Find all Com Ports
        serialPorts = list(list_ports.comports())

        # Find default CLI Port and Data Port
        for port in serialPorts:
            if (
                CLI_XDS_SERIAL_PORT_NAME in port.description
                or CLI_SIL_SERIAL_PORT_NAME in port.description
            ):
                log.info(f"CLI COM Port found: {port.device}")
                self.cliCom.setText(port.device)

        self.core.isGUILaunched = 1
        self.core.changeDemo(self.demoList, self.deviceList, self.gridLayout, self.demoTabs)
        self.core.updateResetButton(self.sensorStop)


     # Start recording Data.
    def startDataRecording(self):
        # 1. Get the duration from the input box
        try:
            duration_sec = float(self.durationEdit.text())
            if duration_sec <= 0: raise ValueError
        except ValueError:
            # Fallback if user types garbage or 0
            duration_sec = 3.0
            self.durationEdit.setText("3")
            log.warning("Invalid duration entered. Defaulting to 3 seconds.")

        # Convert to milliseconds for QTimer
        duration_ms = int(duration_sec * 1000)

        # 2. Set flags and UI state
        self.core.parser.setDataFileBaseName(self.dataFileBaseEdit.text())
        self.core.parser.setSaveData(True)
        
        self.dataRecordButton.setEnabled(False)
        self.dataFileBaseEdit.setEnabled(False)
        self.dataRecordButton.setText(f"Recording ({duration_sec}s)...")
        self.durationEdit.setEnabled(False) # Lock input while recording
        
        self.core.replay = False
        
        # Enable/Disable other UI elements
        self.demoList.setEnabled(True)
        self.deviceList.setEnabled(True)
        self.cliCom.setEnabled(True)
        self.connectButton.setEnabled(True)
        self.filename_edit.setEnabled(True)
        self.selectConfig.setEnabled(True)
        self.start.setText("Start without Send Configuration")
        
        # 3. Start the timer
        self.mdTimer.start(duration_ms)

    #Stop recording data when time ends.
    def stopDataRecording(self):
        self.core.parser.setSaveData(False)
        
        # Reset UI
        self.dataRecordButton.setEnabled(True)
        self.dataFileBaseEdit.setEnabled(True)
        self.dataRecordButton.setText("Record Data")
        self.durationEdit.setEnabled(True) # Unlock input
        
        log.info("Data recording stopped.")


    def initConfigPane(self):
        self.configBox = QGroupBox("Configuration")
        self.selectConfig = QPushButton("Select Configuration")
        self.sendConfig = QPushButton("Start and Send Configuration")
        self.start = QPushButton("Start without Send Configuration")
        self.sensorStop = QPushButton("Send sensorStop Command")
        self.sensorStop.setToolTip("Stop sensor (only works if lowPowerCfg is 0)")
        self.filename_edit = QLineEdit()
        self.selectConfig.clicked.connect(lambda: self.selectCfg(self.filename_edit))
        self.sendConfig.setEnabled(False)
        self.start.setEnabled(False)
        self.sendConfig.clicked.connect(self.sendCfg)
        self.start.clicked.connect(self.startApp)
        self.sensorStop.clicked.connect(self.stopSensor)
        self.sensorStop.setHidden(True)
        self.configLayout = QGridLayout()
        self.configLayout.addWidget(self.filename_edit, 0, 0, 1, 1)
        self.configLayout.addWidget(self.selectConfig, 0, 1, 1, 1)
        self.configLayout.addWidget(self.sendConfig, 1, 0, 1, 2)
        self.configLayout.addWidget(self.start, 2, 0, 1, 2)
        self.configLayout.addWidget(self.sensorStop, 3, 0, 1, 2)
        # self.configLayout.addStretch(1)
        self.configBox.setLayout(self.configLayout)


    def initModePane(self):
        # NAME THE PANE
        self.modeBox = QGroupBox("Data/Model")
        self.modeLayout = QVBoxLayout()

        # RADIO BUTTONS

        self.radio_data_button = QRadioButton("Record Data")
        self.radio_gait_button = QRadioButton("Gait Recognition")

        # MAKE DATA DEFAULT 
        self.radio_data_button.setChecked(True)

        # ADD THE BUTTONS
        self.modeLayout.addWidget(self.radio_data_button)
        self.modeLayout.addWidget(self.radio_gait_button)

        self.radio_data_button.toggled.connect(self.update_mode)
        self.radio_gait_button.toggled.connect(self.update_mode)

        self.modeBox.setLayout(self.modeLayout)


    def update_mode(self):
        if self.radio_gait_button.isChecked():
            self.core.model_enabled = True
            print("Switched to model")
        else: 
            self.core.model_enabled = False
            print("Switched to data collection")

    def displayErrorPopUp(self):
        popUp = QMessageBox.critical(
                self,
                "ERROR",
                "Ensure that the device is in the proper SOP mode after flashing the correct binary, and that the cfg you are sending is valid")
        popUp.exec_()
    

    # Callback function when device is changed
    def onChangeDevice(self):
        self.core.changeDevice(self.demoList, self.deviceList, self.gridLayout, self.demoTabs)
        self.core.updateResetButton(self.sensorStop)

    # Callback function when demo is changed
    def onChangeDemo(self):
        self.core.changeDemo(
            self.demoList, self.deviceList, self.gridLayout, self.demoTabs
        )
        self.sendConfig.setDisabled(0)

        # self.core.changeDevice(self.demoList, self.deviceList, self.gridLayout, self.demoTabs)

    # Callback function when connect button clicked
    def onConnect(self):
        if (self.connectStatus.text() == "Not Connected" or self.connectStatus.text() == "Unable to Connect"):
            if self.core.connectCom(self.cliCom, self.connectStatus) == 0:
                self.connectButton.setText("Reset Connection")
                self.sendConfig.setEnabled(True)
                self.start.setEnabled(True)
            else:
                self.sendConfig.setEnabled(False)
                self.start.setEnabled(False)
        else:
            self.core.gracefulReset()
            self.connectButton.setText("Connect")
            self.connectStatus.setText("Not Connected")
            self.sendConfig.setEnabled(False)
            self.start.setEnabled(False)
            self.send_cfg_first = False
            self.sendConfig.setText("Start and Send Configuration")

            # need to do ser.close()

    # Callback function when 'Select Configuration' is clicked
    def selectCfg(self, filename):
        self.core.selectCfg(filename)

    # Callback function when 'Start and Send Configuration' is clicked
    def sendCfg(self):
        #NICETOHAVE flag to prevent multiple config sends
        if self.send_cfg or self.send_cfg_first:
            return
        
        self.send_cfg = True

        self.sendConfig.setEnabled(False)
        self.start.setEnabled(False)
        self.sendConfig.setText("Sending...")

        QApplication.processEvents()
        self.sendConfig.repaint()

        try:
            self.core.sendCfg()

            if self.core.parser.comError == 1:
                self.core.parser.comError = 0
                self.displayErrorPopUp()
                self.sendConfig.setEnabled(True)
                self.start.setEnabled(True)
            self.send_cfg_first = True
            self.sendConfig.setText("Configuration Sent (reset to resend)")
            self.sendConfig.setEnabled(False)
            self.start.setEnabled(True)
            
        finally:
            self.send_cfg = False
                   
    # Callback function to send sensorStop to device
    def stopSensor(self):
        self.core.stopSensor()
        if(self.core.parser.comError == 1):
            self.core.parser.comError = 0
            self.displayErrorPopUp()

    # Callback function when 'Start without Send Configuration' is clicked
    def startApp(self):
        if (self.core.replay and self.core.playing is False):
            self.start.setText("Pause")
        elif (self.core.replay and self.core.playing is True):
            self.start.setText("Replay")
        self.core.startApp()

class Core:
    def __init__(self):

        self.device = "xWRL6432"
        self.demo = DEMO_OOB_x432

        self.frameTime = 50
        self.parser = UARTParser(type="SingleCOMPort")

        self.replayFile = "replay.json"
        self.replay = False

        self.model_enabled = False
        # set to 1 
        self.isGUILaunched = 0

        self.sl = QSlider(Qt.Horizontal)
        self.sl.valueChanged.connect(self.sliderValueChange)
        self.playing = False
        self.replayFrameNum = 0

        # Populated with each demo and it's corresponding object
        self.demoClassDict = {
            DEMO_OOB_x432: OOBx432()
        }


    def getDemoList(self):
        return DEVICE_DEMO_DICT[self.device]["demos"]

    def getDeviceList(self):
        return list(DEVICE_DEMO_DICT.keys())

    def changeDemo(self, demoList, deviceList, gridLayout, demoTabs):
        self.demo = demoList.currentText()


        permanentWidgetsList = ["Connect to COM Ports", "Configuration", "Tabs", "Replay"]
        # Destroy current contents of graph pane
        for _ in range(demoTabs.count()):
            demoTabs.removeTab(0)
        for i in range(gridLayout.count()):
            try:
                currWidget = gridLayout.itemAt(i).widget()
                if currWidget.title() not in permanentWidgetsList:
                    currWidget.hide()
            except AttributeError as e:
                log.log(0, "Demo Tabs don't have title attribute. This is OK")
                continue

        # Make call to selected demo's initialization function
        if self.demo in self.demoClassDict:
            self.demoClassDict[self.demo].setupGUI(gridLayout, demoTabs, self.device)
            self.cam_tab = CameraTab() 
            demoTabs.addTab(self.cam_tab, "Camera feed")

    def changeDevice(self, demoList, deviceList, gridLayout, demoTabs):
        self.device = deviceList.currentText()

        self.parser.device = self.device


        demoList.clear()
        demoList.addItems(DEVICE_DEMO_DICT[self.device]["demos"])

    def updateResetButton(self, sensorStopButton):
        if DEVICE_DEMO_DICT[self.device]["isxWRLx432"]:
            sensorStopButton.setHidden(True) 
        else:
            sensorStopButton.setHidden(True)

    def stopSensor(self):
        self.parser.sendLine("sensorStop 0")

    def selectFile(self, filename):
        try:
            current_dir = os.getcwd()
            configDirectory = current_dir
        except:
            configDirectory = ""

        fname = QFileDialog.getOpenFileName(caption="Open .cfg File", dir=configDirectory, filter="cfg(*.cfg)")
        filename.setText(str(fname[0]))
        return fname[0]

    def parseCfg(self, fname):
        if (self.replay):
            self.cfg = self.data['cfg']
        else:
            with open(fname, "r") as cfg_file:
                self.cfg = cfg_file.readlines()
                self.parser.cfg = self.cfg
                self.parser.demo = self.demo
                self.parser.device = self.device
        for line in self.cfg:
            args = line.split()
            if len(args) > 0:
                # trackingCfg
                if args[0] == "trackingCfg":
                    if len(args) < 5:
                        log.error("trackingCfg had fewer arguments than expected")
                    else:
                        with suppress(AttributeError):
                            self.demoClassDict[self.demo].parseTrackingCfg(args)
                elif args[0] == "SceneryParam" or args[0] == "boundaryBox":
                    if len(args) < 7:
                        log.error(
                            "SceneryParam/boundaryBox had fewer arguments than expected"
                        )
                    else:
                        with suppress(AttributeError):
                            self.demoClassDict[self.demo].parseBoundaryBox(args)
                elif args[0] == "frameCfg":
                    if len(args) < 4:
                        log.error("frameCfg had fewer arguments than expected")
                    else:
                        self.frameTime = float(args[5]) / 2
                        self.demoClassDict[self.demo].frameTime = self.frameTime
                elif args[0] == "sensorPosition":
                    # sensorPosition for x843 family has 3 args
                    if DEVICE_DEMO_DICT[self.device]["isxWRx843"] and len(args) < 4:
                        log.error("sensorPosition had fewer arguments than expected")
                    elif DEVICE_DEMO_DICT[self.device]["isxWRLx432"] and len(args) < 6:
                        log.error("sensorPosition had fewer arguments than expected")
                    elif DEVICE_DEMO_DICT[self.device]["isxWRLx844"]:
                        self.demoClassDict[self.demo].parseSensorPositionCfg(args)
                    else:
                        with suppress(AttributeError):
                            self.demoClassDict[self.demo].parseSensorPosition(
                                args, DEVICE_DEMO_DICT[self.device]["isxWRx843"]
                            )
                
                # Only used for Small Obstacle Detection
                elif args[0] == "occStateMach":
                    numZones = int(args[1])
                # Only used for Small Obstacle Detection
                elif args[0] == "zoneDef":
                    if len(args) < 8:
                        log.error("zoneDef had fewer arguments than expected")
                    else:
                        with suppress(AttributeError):
                            self.demoClassDict[self.demo].parseBoundaryBox(args)
                elif args[0] == "mpdBoundaryBox":
                    if len(args) < 8:
                        log.error("mpdBoundaryBox had fewer arguments than expected")
                    else:
                        with suppress(AttributeError):
                            self.demoClassDict[self.demo].parseBoundaryBox(args)
                elif args[0] == "chirpComnCfg":
                    if len(args) < 8:
                        log.error("chirpComnCfg had fewer arguments than expected")
                    else:
                        with suppress(AttributeError):
                            self.demoClassDict[self.demo].parseChirpComnCfg(args)
                elif args[0] == "chirpTimingCfg":
                    if len(args) < 6:
                        log.error("chirpTimingCfg had fewer arguments than expected")
                    else:
                        with suppress(AttributeError):
                            self.demoClassDict[self.demo].parseChirpTimingCfg(args)
                elif args[0] == "guiMonitor":
                    if DEVICE_DEMO_DICT[self.device]["isxWRLx432"]:
                        if len(args) < 12:
                            log.error("guiMonitor had fewer arguments than expected")
                        else:
                            with suppress(AttributeError):
                                self.demoClassDict[self.demo].parseGuiMonitor(args)
                elif args[0] == "presenceDetectCfg":
                    with suppress(AttributeError):
                        self.demoClassDict[self.demo].parsePresenceDetectCfg(args)
                elif args[0] == "sigProcChainCfg2":
                    with suppress(AttributeError):
                        self.demoClassDict[self.demo].parseSigProcChainCfg2(args)
                elif args[0] == "mpdBoundaryArc":
                    if len(args) < 8:
                        log.error("mpdBoundaryArc had fewer arguments than expected")
                    else:
                        with suppress(AttributeError):
                            self.demoClassDict[self.demo].parseBoundaryBox(args)
                elif args[0] == "measureRangeBiasAndRxChanPhase":
                    with suppress(AttributeError):
                        self.demoClassDict[self.demo].parseRangePhaseCfg(args)
                elif args[0] == "clutterRemoval":
                    with suppress(AttributeError):
                        self.demoClassDict[self.demo].parseClutterRemovalCfg(args)
                elif args[0] == "sigProcChainCfg":
                    with suppress(AttributeError):
                        self.demoClassDict[self.demo].parseSigProcChainCfg(args)
                elif args[0] == "channelCfg":
                    with suppress(AttributeError):
                        self.demoClassDict[self.demo].parseChannelCfg(args)
                elif args[0] == "SOSOClassifierCfg":
                    with suppress(AttributeError):
                        self.demoClassDict[self.demo].parseSOSOCfg(args)
                elif args[0] == "occupancyBox":
                    with suppress(AttributeError):
                        self.demoClassDict[self.demo].parseOccCfg(args)
                elif args[0] == "intruderDetAdvCfg":
                    with suppress(AttributeError):
                        self.demoClassDict[self.demo].parseDetAdvCfg(args)
                elif args[0] == "cuboidDef":
                    with suppress(AttributeError):
                        self.demoClassDict[self.demo].parseCuboidDef(args)
        # Initialize 1D plot values based on cfg file
        with suppress(AttributeError):
            self.demoClassDict[self.demo].setRangeValues()

    def selectCfg(self, filename):
        try:
            file = self.selectFile(filename)
            self.parseCfg(file)
        except Exception as e:
            log.error(e)
            log.error(
                "Parsing .cfg file failed. Did you select a valid configuration file?"
            )

        log.debug("Demo Changed to " + self.demo)

    def sendCfg(self):
        try:
            if self.demo != "Replay":
                self.parser.sendCfg(self.cfg)
                sys.stdout.flush()
                self.parseTimer.start(int(self.frameTime))  # need this line
        except Exception as e:
            log.error(e)
            log.error("Parsing .cfg file failed. Did you select the right file?")

    def updateGraph(self, outputDict):
        self.demoClassDict[self.demo].updateGraph(outputDict)

    def connectCom(self, cliCom, connectStatus):
        # init threads and timers
        self.uart_thread = parseUartThread(self.parser)

        self.uart_thread.fin.connect(self.updateGraph)
        self.parseTimer = QTimer()
        self.parseTimer.setSingleShot(False)
        self.parseTimer.timeout.connect(self.parseData)
        try:
            if os.name == "nt":
                uart = cliCom.text().strip()
            else:
                uart = cliCom.text().strip()
            self.parser.connectComPort(uart)
            connectStatus.setText("Connected")
        except Exception as e:
            log.error(e)
            connectStatus.setText("Unable to Connect")
            return -1

        return 0

    def startApp(self):
        if (self.replay and self.playing is False):
            self.replayTimer = QTimer()
            self.replayTimer.setSingleShot(True)
            self.replayTimer.timeout.connect(self.replayData)
            self.playing = True
            self.replayTimer.start(100) # arbitrary value to start plotting
        elif (self.replay and self.playing is True):
            self.playing = False
        else :
            self.parseTimer.start(int(self.frameTime))  # need this line, this is for normal plotting



    def replayData(self):
        if (self.playing) :
            outputDict = self.data['data'][self.replayFrameNum]['frameData']
            self.updateGraph(outputDict)
            self.replayFrameNum += 1
            self.sl.setValue(self.replayFrameNum)
            if (self.replayFrameNum < len(self.data['data'])) :
                self.replayTimer.start(self.data['data'][self.replayFrameNum]['timestamp'] - self.data['data'][self.replayFrameNum-1]['timestamp'])

    def sliderValueChange(self):
        self.replayFrameNum = self.sl.value()

    def parseData(self):
        #not lat thread start if already running
        if self.uart_thread.isRunning():
            return
        self.uart_thread.start(priority=QThread.HighestPriority)

    def boardReset(self):
        try:
            base = Path(__file__).resolve().parent          
            xds_dir = base / "reset/uscif/xds110"                       
            exe = xds_dir / "xds110reset.exe"               

            if not exe.exists():
                log.error(f"xds110reset.exe not found: {exe}")
                return

            #cmd = ["wine", str(exe), "--action", "toggle"] #uncoment for linux 
            cmd = [str(exe), "--action", "toggle"]
            subprocess.run(cmd, cwd=str(xds_dir), shell=True, timeout=3, check=False)

            log.info("reset toggle OK")

        except Exception as e:
            log.error(f"Unable to reset the device: {e}")

    def gracefulReset(self):
        self.parseTimer.stop()
        self.uart_thread.stop()
        if self.parser.cliCom is not None:
            self.parser.cliCom.close()
        for demo in self.demoClassDict.values():
            if hasattr(demo, "plot_3d_thread"):
                demo.plot_3d_thread.stop()
            if hasattr(demo, "plot_3d"):
                demo.removeAllBoundBoxes()
            if hasattr(demo, "power_report"):
                demo.resetPowerNumbers()
        self.boardReset()

