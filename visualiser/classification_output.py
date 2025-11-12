import tkinter as tk


class ClassificationOutput:
    def __init__(self, parent):
        self.all_classes = []
        self.current_class = ""
        self._setup_layout(parent)

    def _setup_layout(self, parent):
        """Render the base layout of the whole section"""
        self.frame = tk.Frame(parent, bg="white")
        self.frame.grid_propagate(False)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self._create_title()
        self._create_main_content()

    def _create_title(self):
        """Create the title section"""
        self.title_label = tk.Label(
            self.frame,
            text="Classification Output",
            bg="white",
            font=("Arial", 18, "bold")
        )
        self.title_label.grid(row=0, column=0, sticky="ew", pady=(10, 20))

    def _create_main_content(self):
        """Create all main content sections"""
        self.main_content = tk.Frame(self.frame, bg="white")
        self.main_content.grid(row=1, column=0, sticky="nsew")

        self._configure_main_grid()
        self._create_current_class_section()
        self._create_confidence_bar()
        self._create_other_classes_section()
        self._create_settings()

    def _configure_main_grid(self):
        """Configure grid layout for main content area"""
        self.main_content.grid_rowconfigure(0, minsize=200)  # Current class section
        self.main_content.grid_rowconfigure(1)  # Other classes
        self.main_content.grid_columnconfigure(0, weight=1)

    def _create_current_class_section(self):
        """Create current class display section"""
        self.current_class_frame = tk.Frame(self.main_content, bg="#e3ebf5")
        self.current_class_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(0, 0))

        # Configure grid for section
        self.current_class_frame.grid_rowconfigure(0, weight=1)  # Class label
        self.current_class_frame.grid_rowconfigure(1, minsize=40)  # Confidence bar
        self.current_class_frame.grid_rowconfigure(2)  # Confidence percentage
        self.current_class_frame.grid_columnconfigure(0, weight=1)

        self.current_class_label = tk.Label(
            self.current_class_frame,
            bg="#e3ebf5",
            text=self.current_class,  # Dynamic class name
            font=("Arial", 32, "bold")
        )
        self.current_class_label.grid(row=0, column=0, sticky="nsew")

    def _create_confidence_bar(self):
        """Create confidence bar components"""
        self.confidence_bar_frame = tk.Frame(self.current_class_frame, bg="white")
        self.confidence_bar_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 0))

        self.confidence_filled = tk.Frame(self.confidence_bar_frame, bg="#7da8dc")
        self.confidence_filled.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 0))

        self.confidence_unfilled = tk.Frame(self.confidence_bar_frame, bg="#cadef8")
        self.confidence_unfilled.grid(row=0, column=1, sticky="nsew", padx=0, pady=(0, 0))

        self.confidence_bar_frame.grid_rowconfigure(0, minsize=24)
        self.confidence_bar_frame.grid_columnconfigure(0, weight=1)
        self.confidence_bar_frame.grid_columnconfigure(1, weight=1)

        self.confidence_label = tk.Label(self.current_class_frame, bg="#e3ebf5")
        self.confidence_label.grid(row=2, column=0, sticky="w", padx=0, pady=(0, 10))
        self._set_confidence(0)  # Initial confidence

    def _create_other_classes_section(self):
        """Create other classes display section"""
        self.other_classes_frame = tk.Frame(self.main_content, bg="white")
        self.other_classes_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=10)

        # Configure grid for other classes frame
        self.other_classes_frame.grid_rowconfigure(0, minsize=80)
        self.other_classes_frame.grid_rowconfigure(1, minsize=80)
        self.other_classes_frame.grid_columnconfigure(0, weight=1)
        self.other_classes_frame.grid_columnconfigure(1, weight=1)

        # Create initial other classes
        self._update_other_classes()

    def _create_settings(self):
        """Create settings section"""
        self.settings_frame = tk.Frame(self.main_content, bg="white")
        self.settings_frame.grid(row=2, column=0, sticky="nw", padx=10)

        self.uart_label_text = tk.Label(self.settings_frame, bg="white",
                                        text="UART Port:")
        self.uart_label_text.pack(side="left", padx=5, pady=0)

        self.uart_number = tk.Entry(self.settings_frame, width=4, bg="#eeeeee")
        self.uart_number.pack(side="left", padx=5, pady=0)
        self.uart_number.insert(0, "4")  # Default COM port
        self.uart_number.bind("<Return>", self._on_uart_number_input)
        self.uart_number.bind("<FocusOut>", self._on_uart_number_input)

        self.uart_connected_text = tk.Label(self.settings_frame, bg="white", text="Connected", fg="#008714")
        self.uart_connected_text.pack(side="left", padx=5, pady=0)

    def _on_uart_number_input(self, event):
        """Handle UART number change"""
        if hasattr(self, "on_uart_change"):
            port_number = int(self.uart_number.get())
            connected = self.on_uart_change(port_number)
            if connected:
                self.uart_connected_text.config(text="Connected", fg="#008714")
            else:
                self.uart_connected_text.config(text="Disconnected", fg="#f00")

    def _set_confidence(self, confidence):
        if confidence < 0 or confidence > 100:
            raise ValueError("Confidence must be between 0 and 100.")

        filled_weight = confidence
        unfilled_weight = 100 - confidence

        self.confidence_bar_frame.grid_columnconfigure(0, weight=filled_weight)
        self.confidence_bar_frame.grid_columnconfigure(1, weight=unfilled_weight)
        self.confidence_label.config(text=f"{confidence:.0f}% Confident")

    def _update_current_class(self):
        """Update current class display"""
        self.current_class_label.config(text=self.current_class)

    def _update_other_classes(self):
        """Update other classes display based on current classification"""
        # Clear existing widgets
        for widget in self.other_classes_frame.winfo_children():
            widget.destroy()

        # Create new labels for remaining classes
        other_classes = [cls for cls in self.all_classes if cls != self.current_class]
        for i, class_name in enumerate(other_classes):
            label = tk.Label(
                self.other_classes_frame,
                bg="#f5e8e3",
                text=class_name,
                font=("Arial", 18, "bold")
            )
            row = i // 2
            col = i % 2
            label.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)

    def set_current_classification(self, class_name, confidence):
        """Update current classification and refresh display"""
        if class_name not in self.all_classes:
            raise ValueError(f"Invalid class: {class_name}")

        # Update confidence display
        self._set_confidence(confidence)

        if self.current_class != class_name:
            # Update current class display
            self.current_class = class_name
            self._update_current_class()

            # Update other classes display
            self._update_other_classes()

    def set_class_names(self, class_names, default_class):
        """Set the list of all possible classes"""
        self.all_classes = class_names
        self.current_class = default_class
        self._update_current_class()
        self._update_other_classes()
