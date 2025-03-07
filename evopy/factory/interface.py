import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from pathlib import Path
from evopy.utils.ctk_utils import ParameterWidget
from evopy.factory.base import BaseFactory

class InterfaceFactory(BaseFactory, ctk.CTk):
    appearance: str = "Dark"
    color_config_name: str = "orange"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root: ctk.CTk = ...
        self.comps_frame: ctk.CTkFrame = ...
        self.type_frame: ctk.CTkFrame = ...
        self.params_frame: ctk.CTkFrame = ...
        self.control_frame: ctk.CTkFrame = ...
        self.params_container: ctk.CTkScrollableFrame = ...
        self.component_var: tk.StringVar = ...
        self.types_container: ctk.CTkComboBox = ...
        self.params_container: ctk.CTkScrollableFrame = ...
        self.params_label: ctk.CTkLabel = ...
        self.selected_comp_type: str = ...
        self.comps_widgets: set = set()
        self.type_widgets: set = set()
        self.params_widgets: set = set()
        self.control_widgets: set = set()
        self.types_initialized: bool = False
        self.params_initialized: bool = False

        self.init_display(self.appearance, self.color_config_name)


    def init_display(self, appearance, color_config_name, init_root=True):
        ctk.set_appearance_mode(appearance)
        filepath = Path(__file__).parent / f"{color_config_name}.json"
        ctk.set_default_color_theme(str(filepath))
        if init_root:
            self.root = ctk.CTk()
        self.root.title("Evopy Interface Factory")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.root.destroy())
        self.root.geometry("1400x900")

        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=7)
        self.root.grid_rowconfigure(0, weight=3)
        self.root.grid_rowconfigure(1, weight=6)
        self.root.grid_rowconfigure(2, weight=1)

        self.comps_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.comps_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)

        self.type_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.type_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.params_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.params_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.control_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.control_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(self.comps_frame, text="Components", font=("Arial", 28, "bold")).pack(pady=20)

        self.component_var = tk.StringVar()
        for component_name in self.get_evopy_components():
            ctk.CTkRadioButton(
                self.comps_frame,
                text=f"  {component_name.capitalize()}",
                variable=self.component_var,
                value=component_name,
                command=self.comp_type_selected,
                font=("Lato", 20, "bold"),
            ).pack(anchor="w", pady=10, padx=40)

        ctk.CTkButton(self.control_frame, text="Save Options", command=self.save_options_dialog).pack(padx=10, pady=20)
        ctk.CTkButton(self.control_frame, text="Load Options", command=self.load_options_dialog).pack(padx=10, pady=20)

    def comp_type_selected(self):
        """Handle selection of a component type."""
        component_name = self.component_var.get()
        if not self.types_initialized:
            self.init_type_frame()
        self.types_container.configure(require_redraw=True, values=list(map(lambda x: x.__name__, self.components_classes[component_name])))
        self.types_container.set(self.components_classes[component_name][0].__name__)

    def update_parameters(self, component_name):
        """Display detailed view for a selected component."""

        if not self.params_initialized:
            self.init_params_frame()

        for widget in self.params_container.winfo_children():
            widget.destroy()

        grouped_params = self.get_all_parameters(component_name)
        if not grouped_params:
            self.params_label.configure(text=f"No parameters found for {component_name}")
            return
        self.params_label.configure(text=f"Parameters for {component_name}")
        for source, params in grouped_params:
            source_label = ctk.CTkLabel(self.params_container, text=f"From {source}:", font=("Arial", 16, "bold"))
            source_label.pack(pady=10)

            for param, info in params.items():
                param_type = self.str_to_type(info["type"])
                current_value = self.get_option(param)
                if isinstance(current_value, type):
                    current_value = current_value.__name__
                default_value = self.get_default_value(param)

                if isinstance(default_value, type):
                    choices = self.get_choices(param_type)
                else:
                    choices = None

                ParameterWidget(
                    master=self.params_container,
                    parameter_name=param,
                    current_value=current_value,
                    default_value=default_value,
                    param_type=param_type,
                    choices=choices,
                ).pack(pady=5, padx=10, fill="x")
            self.root.update()

    def init_type_frame(self):
        self.types_initialized = True

        ctk.CTkLabel(self.type_frame, text="Classic Components", font=("Arial", 18)).grid(row=0, column=0, columnspan=3, pady=10)

        ctk.CTkLabel(self.type_frame, text="Class:", font=("Arial", 14)).grid(row=1, column=0, sticky="w", padx=10)

        self.types_container = ctk.CTkComboBox(self.type_frame)
        self.types_container.grid(row=1, column=1, padx=10)

        ctk.CTkButton(self.type_frame, text="Select Existing Component", command=self.select_existing).grid(row=3, column=0, padx=10, pady=10)

        customize_button = ctk.CTkButton(self.type_frame, text="Customize New Component", command=self.customize_new)
        customize_button.grid(row=3, column=1, padx=10, pady=10)
        self.type_widgets.add(customize_button)

    def init_params_frame(self):
        self.params_initialized = True

        self.params_label = ctk.CTkLabel(self.params_frame, text="Editable Parameters", font=("Arial", 18))
        self.params_label.pack(pady=10)

        self.params_container = ctk.CTkScrollableFrame(self.params_frame)
        self.params_container.pack(fill="both", expand=True, padx=10, pady=10)

    def customize_new(self):
        """Handle customization of a new component."""
        component = self.types_container.get()
        #options = self.options.get()
        print(f"Customizing new component: {component} (Options: {None})")
        self.update_parameters(component)

    def select_existing(self):
        """Handle the selection of an existing component."""
        component = self.types_container.get()
        print(f"Selected existing component: {component}")
        self.update_parameters(component)

    def save_options_dialog(self):
        """Save options to a file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Options Files", "*.py")])
        if file_path:
            self.save_options(file_path)

    def load_options_dialog(self):
        """Load options from a file."""
        file_path = filedialog.askopenfilename(filetypes=[("Options Files", "*.py")])
        if file_path:
            self.load_options(file_path)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    factory = InterfaceFactory()
    factory.run()