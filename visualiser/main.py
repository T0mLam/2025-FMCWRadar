import tkinter as tk
import numpy as np
import random 
import serial
import time
from camera_frame import CameraFrame
from classification_output import ClassificationOutput
from point_cloud_graph import PointCloudGraph
from uart_manager import UARTManager

INITIAL_WINDOW_WIDTH = 1290
INITIAL_WINDOW_HEIGHT = 600 


# NEW
USE_UART = True
UART_PORT = "COM6"
UART_BAUDRATE = 1250000
class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("mmWave Radar Visualiser")
        self.root.geometry(f"{INITIAL_WINDOW_WIDTH}x{INITIAL_WINDOW_HEIGHT}")
        
        try:
            self.root.iconbitmap("./icon.ico")
        except tk.TclError:
            print("Warning: Icon file not found. Skipping icon setup.")

        self.root.grid_columnconfigure(0, weight=1, uniform="columns")
        self.root.grid_columnconfigure(1, weight=1, uniform="columns")
        self.root.grid_columnconfigure(2, weight=1, uniform="columns")
        self.root.grid_rowconfigure(0, weight=1)

        self.camera_frame = CameraFrame(self.root)
        self.point_cloud_graph = PointCloudGraph(self.root)
        self.classification_output = ClassificationOutput(self.root)
        
        self.camera_frame.frame.grid(row=0, column=0, sticky="nsew")
        self.point_cloud_graph.frame.grid(row=0, column=1, sticky="nsew")
        self.classification_output.frame.grid(row=0, column=2, sticky="nsew")

        #NEW
        self.mode_frame = tk.Frame(self.root, bg="white")
        self.mode_frame.grid(row=1, column=0, columnspan=3, sticky="ew")

        self.toggle_button = tk.Button(self.mode_frame, text="Switch to UART mode" if not USE_UART else "Switch to fake data", command=self.toggle_mode, bg="#ddd", font=("Arial", 12, "bold"))
        self.toggle_button.pack(pady=10)
        #END NEW

        self.classification_output.set_class_names(["STOOD", "SAT", "LYING", "SITTING", "FALLING"], "STOOD")

        self.uart_manager = None
        self.classification_output.uart_connected_text.config(text="No UART (fake data)", fg = "#f00")
        if USE_UART:
            self.setup_uart_mode()
        else:
            self.setup_fake_data_mode()
        if not USE_UART:
            self.root.after(1000,self.fake_data_loop)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def schedule_classification_update(self, class_name, confidence):
        self.root.after(0, self.handle_classification_update, class_name, confidence)

    def schedule_point_cloud_update(self, data):
        self.root.after(0, self.handle_point_cloud_update, data)

    def handle_classification_update(self, class_name, confidence):
        self.classification_output.set_current_classification(class_name, confidence)

    def handle_point_cloud_update(self, data):
        self.point_cloud_graph.update_graph(data)
        self.camera_frame.overlay_points(data)
    def fake_data_loop(self):
        fake_data = generate_fake_point_cloud()
        self.handle_point_cloud_update(fake_data)
        self.root.after(100,self.fake_data_loop)
    def change_uart_port(self, port_number):
        port_number = int(port_number)
        if port_number < 0:
            raise ValueError("Port number must be non-negative.")
        new_port = f"COM{port_number}"
        self.uart_manager.close()
        self.uart_manager.port = new_port
        connected = self.uart_manager.connect()
        self.uart_manager.start_parsing()

        return connected

    def generate_fake_point_cloud(self, num_points=25):
        """
        Simulate fake radar points (Y, Z in meters).
        """
        return np.array([
            [random.uniform(-1.5, 1.5), random.uniform(-1.0, 1.0)]
            for _ in range(num_points)
        ])
    
    
    #NEW
    def setup_uart_mode(self):
        """
        Connect to radar over UART
        """
        #send_config("COM6", 'config.cfg')
        #time.sleep(1)
        self.uart_manager = UARTManager(UART_PORT, UART_BAUDRATE)
        self.uart_manager.on_classification_updated = self.schedule_classification_update
        self.uart_manager.on_point_cloud_updated = self.schedule_point_cloud_update

        connected = self.uart_manager.connect()

        if connected:
            print("connected to uart port")
            self.uart_manager.start_parsing()
            self.classification_output.uart_connected_text.config(text="Connected", fg="#008714")
        else:
            print("failed to connect")
            self.classification_output.uart_connected_text.config(text="Disconnected", fg="#f00")
    
    #NEW
    def setup_fake_data_mode(self):
        self.uart_manager = None
        self.classification_output.uart_connected_text.config(text="No UART (fake data)", fg="#f00")
        self.root.after(1000, self.fake_data_loop)

    def toggle_mode(self):
        """
        Switch between UART and fake data mode
        """
        global USE_UART
        USE_UART = not USE_UART

        if self.uart_manager:
            try:
                self.uart_manager.close()
            except Exception:
                pass
        self.camera_frame.stop_feed()
        self.camera_frame._start_feed(0)

        if USE_UART:
            self.setup_uart_mode()
            self.toggle_button.config(text="Switch to fake data")
        else:
            self.setup_fake_data_mode()
            self.toggle_button.config(text="Switch to UART mode")


    #NEW
    def fake_data_loop(self):
        """Periodically update the overlay and graph with fake data."""
        fake_data = self.generate_fake_point_cloud()
        self.handle_point_cloud_update(fake_data)
        self.root.after(100, self.fake_data_loop)  # update every 100ms
    #NEW
    def on_close(self):
        print("Stopping camera feed")
        self.camera_frame.stop_feed()
        if self.uart_manager:
            print("Closing UART Manager")
            try:
                self.uart_manager.close()
            except Exception:
                pass
        print("Exiting Tkinter loop")
        self.root.quit()
        self.root.destroy()
        print("Shutdown complete")

    def run(self):
        self.root.mainloop()

#NEW
def send_config(cli_port="COM6", config_path="config.cfg"):
    try:
        with serial.Serial(cli_port, 115200, timeout=0.5) as cli:
            with open(config_path, 'r') as cfg:
                for line in cfg:
                    line = line.strip()
                    if line and not line.startswith('%'):
                        cli.write((line + '\n').encode())
                        time.sleep(0.05)

            print("Config sent!")
    except Exception as e:
        print(f"Config send failed! : {e}")
def generate_fake_point_cloud(num_points=20):
    return np.array([[random.uniform(-1,1), random.uniform(-1,1)] for _ in range(num_points)])


if __name__ == "__main__":
    app = MainWindow()
    app.run()
