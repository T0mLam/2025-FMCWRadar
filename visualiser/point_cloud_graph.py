import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


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


class PointCloudGraph:
    def __init__(self, parent):
        self.buffer = CircularBuffer(5)
        self.frame = tk.Frame(parent, bg="white")
        self.frame.grid_propagate(False)

        # Title
        self.title_label = tk.Label(self.frame, text="Point Cloud Data", bg="white", font=("Arial", 18, "bold"))
        self.title_label.grid(row=0, column=0, sticky="ew", pady=(10, 20))

        # Configure grid
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # Setup graph
        self.fig = Figure(layout='constrained')
        self.plot = self.fig.add_subplot(111)
        self.plot.set_xlabel('Y-Axis')
        self.plot.set_ylabel('Z-Axis')
        self.plot.axis([2, 4, -2, 2])
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        self.scatter_plot = self.plot.scatter([0], [0])

    def update_graph(self, data):
        """Update the graph with new data"""
        self.buffer.add(data[:, 0], data[:, 1])
        self.scatter_plot.set_offsets(np.c_[self.buffer.get_x(), self.buffer.get_y()])
        self.canvas.draw()


