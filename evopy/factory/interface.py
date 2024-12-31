import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from pathlib import Path
from evopy.utils.ctk_utils import ParameterWidget
from evopy.factory.base import BaseFactory
from evopy.environment import BaseEnvironment
from evopy.evaluator import ChainEvaluator


class InterfaceFactory(BaseFactory):
    def __init__(self):
        super().__init__()

        # Configure CustomTkinter
        ctk.set_appearance_mode("Dark")
        # Get file path
        file_path = Path(__file__).resolve().parent / "breeze.json"
        
        ctk.set_default_color_theme(file_path)

        # Create the root window
        self.root = ctk.CTk()
        self.root.title("Evopy Interface Factory")
        self.root.geometry("1400x900")

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

        # Top Section: Component Info
        self.component_info_frame = ctk.CTkFrame(self.details_frame, corner_radius=15)
        self.component_info_frame.pack(fill="x", padx=10, pady=10)

        self.info_label = ctk.CTkLabel(self.component_info_frame, text="Component Details", font=("Arial", 18))
        self.info_label.grid(row=0, column=0, columnspan=3, pady=10)

        self.component_type_label = ctk.CTkLabel(self.component_info_frame, text="Component Type:", font=("Arial", 14))
        self.component_type_label.grid(row=1, column=0, sticky="w", padx=10)

        self.component_type_dropdown = ctk.CTkComboBox(
            self.component_info_frame, values=list(self.options_summary.keys()), command=self.on_type_selected
        )
        self.component_type_dropdown.grid(row=1, column=1, padx=10)

        self.component_version_label = ctk.CTkLabel(self.component_info_frame, text="Version:", font=("Arial", 14))
        self.component_version_label.grid(row=2, column=0, sticky="w", padx=10)

        self.version_entry = ctk.CTkEntry(self.component_info_frame, placeholder_text="Enter version")
        self.version_entry.grid(row=2, column=1, padx=10)

        self.existing_button = ctk.CTkButton(self.component_info_frame, text="Select Existing Component", command=self.select_existing)
        self.existing_button.grid(row=3, column=0, padx=10, pady=10)

        self.customize_button = ctk.CTkButton(self.component_info_frame, text="Customize New Component", command=self.customize_new)
        self.customize_button.grid(row=3, column=1, padx=10, pady=10)

        # Bottom Section: Parameter Details
        self.parameters_label = ctk.CTkLabel(self.details_frame, text="Editable Parameters", font=("Arial", 18))
        self.parameters_label.pack(pady=10)

        self.parameters_container = ctk.CTkScrollableFrame(self.details_frame)
        self.parameters_container.pack(fill="both", expand=True, padx=10, pady=10)

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
                font=("Arial", 20),
            )
            rb.pack(anchor="w", pady=10, padx=25)

    def on_type_selected(self, component_name):
        """Handle selection of a component type."""
        self.show_details(component_name)

    def select_existing(self):
        """Handle the selection of an existing component."""
        component = self.component_type_dropdown.get()
        version = self.version_entry.get()
        print(f"Selected existing component: {component} (Version: {version})")
        self.show_details(component)

    def customize_new(self):
        """Handle customization of a new component."""
        component = self.component_type_dropdown.get()
        version = self.version_entry.get()
        print(f"Customizing new component: {component} (Version: {version})")
        self.show_details(component)

    def show_details(self, component_class):
        """Display detailed view for a selected component."""
        # Clear parameters container
        component_name = component_class#.__name__
        for widget in self.parameters_container.winfo_children():
            widget.destroy()
            
        grouped_params = self.get_all_parameters(BaseEnvironment)
        if not grouped_params:
            self.parameters_label.configure(text=f"No Parameters Found for {component_name}")
            return

        self.parameters_label.configure(text=f"Parameters for {component_name}")


        for source, params in grouped_params:
            # Add a label for the source
            source_label = ctk.CTkLabel(self.parameters_container, text=f"From {source}:", font=("Arial", 16, "bold"))
            source_label.pack(pady=10)

            # Display each parameter
            for param in params:
                current_value = self.get_option(param)
                default_value = self.get_default_value(param)
                param_type = self.get_option_type(param)

                widget = ParameterWidget(
                    master=self.parameters_container,
                    parameter_name=param,
                    current_value=current_value,
                    default_value=default_value,
                    param_type=param_type,
                )
                widget.pack(pady=5, padx=10, fill="x")
                # param_frame = ctk.CTkFrame(self.parameters_container, corner_radius=15)
                # param_frame.pack(fill="x", padx=10, pady=5)
                # param_info = self.describe_option(param)
                # label = ctk.CTkLabel(param_frame, text=f"{param}: {param_info.get('type', 'Unknown')}", font=("Arial", 14))
                # label.grid(row=0, column=0, sticky="w", padx=10)
                # default_value = self.options_default.get(param, "N/A")
                # current_value = self.options.get(param, "Not Set")
                # is_modified = current_value != default_value

                # value_entry = ctk.CTkEntry(param_frame, placeholder_text=str(current_value), width=200)
                # value_entry.grid(row=0, column=1, padx=10)

                # status_label = ctk.CTkLabel(
                #     param_frame,
                #     text=f"{'Modified' if is_modified else 'Default'}",
                #     font=("Arial", 12),
                #     text_color="green" if is_modified else "gray",
                # )
                # status_label.grid(row=0, column=2, padx=10)


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
