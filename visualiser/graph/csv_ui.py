import tkinter as tk
from tkinter import filedialog
import visualiser
import time
import math

INITIAL_WINDOW_WIDTH = 800
INITIAL_WINDOW_HEIGHT = 900


class MainWindow:
    def __init__(self):
        self.curr_id = None
        self.paused = False
        self.root = tk.Tk()
        self.root.title("mmWave CSV File Viewer")
        self.root.geometry(f"{INITIAL_WINDOW_WIDTH}x{INITIAL_WINDOW_HEIGHT}")
        self.root.iconbitmap("./icon.ico")
        self.root.config(bg="white")

        self.root.grid_columnconfigure(0, weight=1, uniform="columns")
        self.root.grid_columnconfigure(1, weight=1, uniform="columns")
        self.root.grid_rowconfigure(0, weight=25)
        self.root.grid_rowconfigure(1, weight=1)

        # This frame holds the checkbox and the open file button
        self.option_frame = tk.Frame(self.root, bg="white")
        self.option_frame.grid_columnconfigure(0, weight=1)
        self.option_frame.grid_columnconfigure(1, weight=1)
        self.option_frame.grid_rowconfigure(0, weight=1)
        self.option_frame.grid(row=1, column=1, sticky="e", padx=(0, 15))

        self.button_open = tk.Button(self.option_frame, text="Open CSV File", cursor="hand2",
                                     command=self.open_file, font=("Arial", 10))
        self.button_open.grid(row=0, column=1, sticky="e", padx=5, pady=20, ipady=10, ipadx=10)

        # Create an IntVar to store the checkbox state (0 = unchecked, 1 = checked)
        self.buff_on = tk.IntVar()

        # Create a checkbox
        checkbox = tk.Checkbutton(self.option_frame, text="Enable Circular Buffer",
                                  variable=self.buff_on, font=("Arial", 10), bg="white")
        checkbox.grid(row=0, column=0, sticky="w", padx=5)

        # This frame holds the pause/resume text and also the info icon
        self.pause_frame = tk.Frame(self.root, bg="white")
        self.pause_frame.grid_columnconfigure(0, weight=1)
        self.pause_frame.grid_columnconfigure(1, weight=1)
        self.pause_frame.grid_rowconfigure(0, weight=1)
        self.pause_frame.grid(row=1, column=0, sticky="w", padx=(15, 0))

        # Informs the user telling them whether a file is being visualised and whether it is paused or not
        self.pause_text = tk.Label(self.pause_frame, text="Select a file to display", font=("Arial", 11, "bold"),
                                   bg="white", fg="black")
        self.pause_text.grid(column=0, row=0, sticky="w", padx=5)

        # Help icon
        image = tk.PhotoImage(file="info_icon.png")
        self.help_icon = tk.Label(self.pause_frame, image=image, cursor="hand2", bg="white", fg="white")
        self.image = image
        self.help_icon.grid(column=1, row=0, sticky="e", padx=5)

        # Tooltip label (hidden by default), this gives directions to the user
        self.tooltip_label = tk.Label(self.root, text="Select a file to visualise using the button on the right.",
                                      bg="yellow", relief="solid", bd=1, font=("Arial", 10), padx=5, pady=5)
        self.tooltip_label.place_forget()

        # Bind hover events
        self.help_icon.bind("<Enter>", self.show_tooltip)
        self.help_icon.bind("<Leave>", self.hide_tooltip)

        # Bind pause button
        self.root.bind("<space>", self.pause_display)

        # Opens an empty file
        displayed_file = visualiser.CsvData("")
        self.displayed_data = displayed_file.read_file()
        self.point_cloud_graph = visualiser.DataVisualizer(self.root, self.displayed_data)
        self.point_cloud_graph.tk_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=100, pady=10)
        self.update_frame()

    def show_tooltip(self, event):
        # For the info icon
        self.tooltip_label.lift()  # Bring to the front
        self.tooltip_label.place(x=self.help_icon.winfo_x() + 25, y=self.pause_frame.winfo_y() - 25)

    def hide_tooltip(self, event):
        # For the info icon
        self.tooltip_label.place_forget()

    def update_frame(self):
        if self.paused:
            self.curr_id = self.root.after(1000, self.update_frame)
            return

        # Records how long computations take so that frame rate can be calculated consistently
        start_time = time.perf_counter()

        # The way data is visualised is changed depending on whether the checkbox is marked or not
        if self.buff_on.get():
            self.point_cloud_graph.update_graph(self.displayed_data)
        else:
            self.point_cloud_graph.update_graph(self.displayed_data, False)
        end_time = time.perf_counter()
        frame_diff = self.point_cloud_graph.curr_frame - self.point_cloud_graph.frame

        # Calculate how long to wait for
        time_to_wait = max(1, frame_diff) * (1 / self.point_cloud_graph.fps) - (end_time - start_time)

        if time_to_wait <= 0:
            time_to_wait = 0
        if not self.point_cloud_graph.finish:
            self.curr_id = self.root.after(math.floor(time_to_wait * 1000), self.update_frame)
        else:
            self.pause_text.config(text="Select a file to display", fg="black")
            self.tooltip_label.config(text="Select a file to visualise using the button on the right")

    def pause_display(self, event=None):
        if self.point_cloud_graph.finish:
            return
        if not self.paused:
            print("Paused")
            self.pause_text.config(text="Paused", fg="red")
            self.tooltip_label.config(text="Press space to resume the visualisation")
            self.paused = True
        else:
            print("Continue")
            self.pause_text.config(text="Playing", fg="green")
            self.tooltip_label.config(text="Press space to pause the visualisation")
            self.paused = False

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a CSV File",
            filetypes=[("CSV files", "*.csv")],  # Restrict to CSV files only
            defaultextension=".csv"  # Default file type
        )
        # If no file is selected, exit out of the function
        if len(file_path) == 0:
            return

        # Read and store the CSV data as an array
        displayed_file = visualiser.CsvData(file_path)
        self.displayed_data = displayed_file.read_file()

        # If there are any ongoing frame updates scheduled cancel them
        if self.curr_id:
            self.root.after_cancel(self.curr_id)

        # Gets the file name
        self.point_cloud_graph.new_graph(displayed_file.filename.split("/")[-1])
        self.paused = True
        self.pause_display()

        # Schedules a frame updated
        self.update_frame()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()
