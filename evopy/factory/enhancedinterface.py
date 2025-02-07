import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from pathlib import Path
from evopy.utils.ctk_utils import ParameterWidget
from evopy.factory.base import BaseFactory
from evopy.environment import BaseEnvironment
from evopy.evaluator import ChainEvaluator


class EnhancedInterfaceFactory(BaseFactory):
    def __init__(self):
        super().__init__()

        # Configure CustomTkinter
        ctk.set_appearance_mode("Dark")
        file_path = Path(__file__).resolve().parent / "breeze.json"
        ctk.set_default_color_theme(file_path)

        # Create the root window
        self.root = ctk.CTk()
        self.root.title("Enhanced Evopy Interface Factory")
        self.root.geometry("1600x1000")

        # Configure grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)  # Sidebar
        self.root.grid_columnconfigure(1, weight=4)  # Content frame

        # Sidebar Frame
        self.nav_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.nav_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.nav_label = ctk.CTkLabel(self.nav_frame, text="Components", font=("Arial", 28, "bold"))
        self.nav_label.pack(pady=10)

        self.component_var = tk.StringVar()
        self.populate_navigation()

        # Content Frame
        self.details_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.details_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Top Section: Component Class Selector
        self.class_selector_frame = ctk.CTkFrame(self.details_frame, corner_radius=15)
        self.class_selector_frame.pack(fill="x", padx=10, pady=10)

        self.class_selector_label = ctk.CTkLabel(
            self.class_selector_frame, text="Select or Customize Component Class", font=("Arial", 18)
        )
        self.class_selector_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.component_class_dropdown = ctk.CTkComboBox(
            self.class_selector_frame, values=[], command=self.on_class_selected
        )
        self.component_class_dropdown.grid(row=1, column=0, padx=10, pady=10)

        self.customize_class_button = ctk.CTkButton(
            self.class_selector_frame, text="Customize", command=self.customize_class
        )
        self.customize_class_button.grid(row=1, column=1, padx=10, pady=10)

        # Middle Section: Parameter Details
        self.parameters_label = ctk.CTkLabel(self.details_frame, text="Editable Parameters", font=("Arial", 18))
        self.parameters_label.pack(pady=10)

        self.parameters_container = ctk.CTkScrollableFrame(self.details_frame)
        self.parameters_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Restore and Save Buttons
        self.restore_all_button = ctk.CTkButton(self.details_frame, text="Restore All Parameters", command=self.restore_all_parameters)
        self.restore_all_button.pack(pady=5)

        # Bottom Buttons
        self.save_button = ctk.CTkButton(self.root, text="Save Options", command=self.save_options)
        self.save_button.grid(row=1, column=0, columnspan=2, sticky="we", padx=10, pady=5)

        self.load_button = ctk.CTkButton(self.root, text="Load Options", command=self.load_options)
        self.load_button.grid(row=2, column=0, columnspan=2, sticky="we", padx=10, pady=5)

    def populate_navigation(self):
        """Populate the sidebar with radio buttons for navigation."""
        for component_name in self.components_types:
            rb = ctk.CTkRadioButton(
                self.nav_frame,
                text=component_name,
                variable=self.component_var,
                value=component_name,
                command=lambda name=component_name: self.show_details(name),
                font=("Lato", 20, "bold"),
            )
            rb.pack(anchor="w", pady=10, padx=25)

    def on_class_selected(self, class_name):
        print(f"Class selected: {class_name}")

    def customize_class(self):
        print("Customizing class...")

    def restore_all_parameters(self):
        print("Restoring all parameters to default values...")

    def save_options(self):
        """Save options to a file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Options Files", "*.py")])
        if file_path:
            print(f"Options saved to {file_path}")

    def load_options(self):
        """Load options from a file."""
        file_path = filedialog.askopenfilename(filetypes=[("Options Files", "*.py")])
        if file_path:
            print(f"Options loaded from {file_path}")

    def run(self):
        self.root.mainloop()
