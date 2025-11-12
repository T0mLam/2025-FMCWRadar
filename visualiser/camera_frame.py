import tkinter as tk
from tkinter import ttk

import cv2
from PIL import Image, ImageTk

INITIAL_WINDOW_WIDTH = 1290
INITIAL_WINDOW_HEIGHT = 600


class CameraFrame:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="white")
        self.frame.grid_propagate(False)

        # Title
        self.title_label = tk.Label(self.frame, text="Camera", bg="white", font=("Arial", 18, "bold"))
        self.title_label.grid(row=0, column=0, sticky="ew", pady=(10, 20))

        self.cap = None
        self.after_id = None
        self.current_loop_id = None
        self.available_webcams = self._get_available_webcams()

        # Setup frame grid
        self.frame.grid_rowconfigure(1, weight=1)  # For webcam label
        self.frame.grid_rowconfigure(2, weight=0)  # For selector
        self.frame.grid_columnconfigure(0, weight=1)

        if not self.available_webcams:
            # Display no camera connected message
            self.no_camera_label = tk.Label(self.frame, bg="white", text="No camera connected",
                                            fg="red", font=("Arial", 16))
            self.no_camera_label.grid(row=1, column=0, sticky="nsew")
        else:
            # Display webcam feed
            self.webcam_label = tk.Label(self.frame, bg="white")
            self.webcam_label.grid(row=1, column=0, sticky="nsew")

            self.selector_frame = tk.Frame(self.frame, bg="white")
            self.selector_frame.grid(row=2, column=0, sticky="ew")

            self.webcam_label_text = tk.Label(self.selector_frame, bg="white",
                                              text="Select Webcam:")
            self.webcam_label_text.pack(side="left", padx=5, pady=20)

            self.webcam_selector = ttk.Combobox(self.selector_frame, state="readonly")
            self.webcam_selector.pack(side="left", padx=5, pady=20)
            self.webcam_selector["values"] = self.available_webcams
            self.webcam_selector.current(0)
            self.webcam_selector.bind("<<ComboboxSelected>>", self._on_webcam_select)

            self._start_feed(0)

    @staticmethod
    def _get_available_webcams():
        # Suppress OpenCV log messages
        original_log_level = cv2.getLogLevel()
        cv2.setLogLevel(0)

        # Detect available webcams
        index = 0
        webcams = []
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                cap.release()
                break
            webcams.append(f"Webcam {index + 1}")
            cap.release()
            index += 1

        # Restore original log level
        cv2.setLogLevel(original_log_level)

        return webcams

    def _start_feed(self, index):
        self.stop_feed()
        self.current_loop_id = id(object())
        self.cap = cv2.VideoCapture(index)
        self._update_frame(self.current_loop_id)

    def stop_feed(self):
        # Cancel the next frame update
        if self.after_id:
            self.frame.after_cancel(self.after_id)
            self.after_id = None
        # Release the webcam
        if self.cap:
            self.cap.release()
            self.cap = None

    def _on_webcam_select(self, event):
        selected_index = self.webcam_selector.current()
        self._start_feed(selected_index)

    def _update_frame(self, loop_id):
        if loop_id != self.current_loop_id or not self.cap:
            return

        ret, frame = self.cap.read()
        if ret:
            label_width = self.webcam_label.winfo_width()
            label_height = self.webcam_label.winfo_height()

            if label_width > 1 and label_height > 1:  # Wait for the GUI to have loaded
                # Resize camera view
                height, width, _ = frame.shape
                frame_aspect = width / height
                label_aspect = label_width / label_height

                if frame_aspect > label_aspect:
                    new_height = label_height
                    new_width = int(new_height * frame_aspect)
                else:
                    new_width = label_width
                    new_height = int(new_width / frame_aspect)
                frame = self.draw_overlay(frame) 
                frame = cv2.resize(frame, (new_width, new_height))
                x_offset = max(0, (new_width - label_width) // 2)
                y_offset = max(0, (new_height - label_height) // 2)
                frame = frame[y_offset:y_offset + label_height, x_offset:x_offset + label_width]

                # Render in Tkinter
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.webcam_label.imgtk = imgtk
                self.webcam_label.config(image=imgtk)

        # Schedule the next frame update
        self.after_id = self.frame.after(10, self._update_frame, loop_id)
    
    def overlay_points(self,points):
        """
        Store radar points for overlay
        """
        self.overlay_points_data = points
    
    def draw_overlay(self,frame):
        """
        Draw the radar points onto the frame
        """
        if not hasattr(self, 'overlay_points_data'):
            return frame
        points = self.overlay_points_data

        if points is None or len(points) == 0:
            return frame
        height, width, _ = frame.shape

        scale = 100

        offset_x, offset_y = width // 2, height // 2

        for y,z in points:
            px = int(offset_x + y * scale)
            py = int(offset_y - z * scale)
            cv2.circle(frame, (px,py), 5, (0,0,255), -1)

        return frame

