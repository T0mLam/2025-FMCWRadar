import csv
from pprint import pprint

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import tkinter as tk


class CircularBuffer:
    def __init__(self, capacity):
        self.list_x = [[1000]] * capacity
        self.list_y = [[1000]] * capacity
        self.cap = capacity
        self.ptr = 0

    def add(self, data_x, data_y):
        self.list_x[self.ptr] = data_x
        self.list_y[self.ptr] = data_y
        self.ptr += 1
        if self.ptr >= self.cap:
            self.ptr = 0

    def get_x(self):
        res = []
        for data_block in self.list_x:
            for data in data_block:
                res.append(data)
        return res

    def get_y(self):
        res = []
        for data_block in self.list_y:
            for data in data_block:
                res.append(data)
        return res

    def empty_buff(self):
        self.list_x = [[1000]] * self.cap
        self.list_y = [[1000]] * self.cap


class CsvData:
    filename = 'blank'

    def __init__(self, filename=""):
        # Prevents issues like filename.csv.csv when opening files
        if filename.endswith('.csv'):
            self.filename = filename[:-4]
        else:
            self.filename = filename

    def read_file(self):
        np.set_printoptions(suppress=True)
        point_cloud_mat = []

        # If file selected has no name, display empty array
        if len(self.filename) == 0:
            return np.array([[0, 1000, 1000, 1000]])

        filename = self.filename + '.csv'
        with open(filename, mode='r') as file:
            csv_file = csv.reader(file)
            # Skip the header
            next(csv_file)
            for lines in csv_file:
                frameCount = lines[0]
                i = 8
                pprint(frameCount)
                while i < len(lines):
                    position_val = [frameCount] + lines[i:(i + 3)]
                    # Don't append points which have their z-coordinate missing
                    if not len(position_val) % 4:
                        point_cloud_mat.append(position_val)
                    i += 3

        # If the csv file given was empty, display dummy data which is out of bounds
        if not point_cloud_mat:
            return np.array([[0, 1000, 1000, 1000]])

        point_cloud_mat = np.array(point_cloud_mat).reshape(-1, 4)
        pprint(point_cloud_mat)
        point_cloud_mat = point_cloud_mat.astype(np.float64)
        return point_cloud_mat


class DataVisualizer:
    def __init__(self, parent, data, fps=10):
        self.frame = None
        self.sitting_data = data
        self.fps = fps
        self.buffer = CircularBuffer(5)
        self.finish = False

        # UI
        self.tk_frame = tk.Frame(parent, bg="white")
        self.tk_frame.grid_propagate(False)

        # Title
        self.title_label = tk.Label(self.tk_frame, text="", bg="white", font=("Arial", 18, "bold"))
        self.title_label.grid(row=0, column=0, sticky="ew", pady=(10, 20))

        # Configure grid
        self.tk_frame.grid_rowconfigure(1, weight=1)
        self.tk_frame.grid_columnconfigure(0, weight=1)

        # Setup graph
        self.fig = Figure(layout='constrained')
        self.plot = self.fig.add_subplot(111)
        self.plot.set_xlabel('Y-Axis')
        self.plot.set_ylabel('Z-Axis')
        self.plot.axis([2, 4, -2, 2])
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tk_frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", pady=(0, 20))

        self.scatter_plot = self.plot.scatter([0], [0])

        # Get axis limits
        xlim = self.plot.get_xlim()
        ylim = self.plot.get_ylim()

        # Add frame count
        self.frame_count = self.plot.text(xlim[1], ylim[0], "Frame Count: 0",
                                          horizontalalignment='right', verticalalignment='bottom',
                                          fontsize=12, color='black')

        self.curr_frame = self.start = self.end = 0

    def update_graph(self, data, buffer_on=True):
        """Update the graph with new data"""
        self.frame = data[self.start, 0]
        print(self.frame)

        while self.curr_frame < self.frame + 1:
            if self.end >= len(data) - 1:
                print("End of file reached.")
                self.finish = True
                break
            self.end += 1
            self.curr_frame = data[self.end, 0]

        frame_to_plot = data[self.start:self.end, :]
        y = frame_to_plot[:, 1].flatten()
        z = frame_to_plot[:, 2].flatten()

        self.buffer.add(y, z)
        if buffer_on:
            self.scatter_plot.set_offsets(np.c_[self.buffer.get_x(), self.buffer.get_y()])
        else:
            self.scatter_plot.set_offsets(np.c_[y, z])
        self.frame_count.set_text(f"Frame Count: {int(self.frame)}")

        self.start = self.end
        self.canvas.draw()

    def new_graph(self, title):
        # When opening a new csv file this function is called, restarting all variables to their initial state
        self.curr_frame = self.start = self.end = 0
        # Changes the title to the file name which is passed as a parameter
        self.title_label.config(text=title)
        self.buffer.empty_buff()
        self.finish = False
