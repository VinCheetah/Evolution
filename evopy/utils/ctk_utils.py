import customtkinter as CTk
from typing import Union, Callable
from math import inf



class Spinbox(CTk.CTkFrame):
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 step_size: Union[int, float] = 1,
                 default_value: Union[int, float] = 0,
                 command: Callable = None,
                 **kwargs):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = step_size
        self.command = command

        self.configure(fg_color=("gray78", "gray28"))  # set frame color

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = CTk.CTkButton(self, text="-", width=height-6, height=height-6,
                                                       command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = CTk.CTkEntry(self, width=width-(2*height), height=height-6, border_width=0)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")
        self.entry.bind("<Enter>", lambda event: self.entry.focus_set())
        self.entry.bind("<Escape>", lambda event: self.entry.focus_set())
        self.entry.bind("<FocusOut>", self.command)
        self.entry.bind("<ButtonRelease-1>", self.command)

        self.add_button = CTk.CTkButton(self, text="+", width=height-6, height=height-6,
                                                  command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        self.set_value(default_value)
        
    def _get(self) -> Union[float, int, None]:
        return float(self.entry.get())
    
    def get(self) -> Union[float, int, None]:
        try:
            return self._get()
        except ValueError:
            return None
        
    def left_transform(self) -> Union[float, int, None]:
        try:
            return self._left_transform()
        except ValueError:
            return None
        
    def _left_transform(self) -> Union[float, int, None]:
        return self.get() - self.step_size
    
    def right_transform(self) -> Union[float, int, None]:
        try:
            return self._right_transform()
        except ValueError:
            return None
        
    def _right_transform(self) -> Union[float, int, None]:
        return self.get() + self.step_size

    def add_button_callback(self):
        try:
            self.set_value(self.right_transform())
        except ValueError:
            pass
        if self.command is not None:
            self.command()

    def subtract_button_callback(self):
        try:
            self.set_value(self.left_transform())
        except ValueError:
            pass
        if self.command is not None:
            self.command()

    def set_value(self, value: Union[float, int]):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))
        
        

class IntSpinbox(Spinbox):
    
    def _get(self) -> int:
        return int(super()._get())
    
class FloatSpinbox(Spinbox):

    def __init__(self, *args, step_size=0.1, **kwargs) -> None:
        super().__init__(*args, step_size=step_size, **kwargs)
    
    def _get(self) -> float:
        return round(float(super()._get()), 8)
    
class BoundedSpinbox(Spinbox):
    
    def __init__(self, *args, width = 100, height = 32, step_size = 1, default_value = 0, command = None, min_value=-inf, max_value=inf, **kwargs):
        super().__init__(*args, width=width, height=height, step_size=step_size, default_value=default_value, command=command, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        
    def _left_transform(self) -> Union[float, int, None]:
        return max(self.min_value, self.get() - self.step_size)
    
    def _right_transform(self) -> Union[float, int, None]:
        return min(self.max_value, self.get() + self.step_size)
    
class BoundedIntSpinbox(BoundedSpinbox, IntSpinbox):
    
    def __init__(self, *args, width=100, height=32, step_size=1, default_value=0, command=None, min_value=-inf, max_value=inf, **kwargs):
        super().__init__(*args, width=width, height=height, step_size=step_size, default_value=default_value, command=command, min_value=min_value, max_value=max_value, **kwargs)
    
class BoundedFloatSpinbox(BoundedSpinbox, FloatSpinbox):

    def __init__(self, *args, step_size=0.1, **kwargs):
        super().__init__(*args, step_size=step_size, **kwargs)
        
    



class FolderSystem(CTk.CTkScrollableFrame):
    """Custom folder navigation system with support for subfolders."""

    def __init__(self, master, options_summary, callback, **kwargs):
        super().__init__(master, **kwargs)
        self.options_summary = options_summary
        self.callback = callback
        self.folder_widgets = {}
        self.build_folders(options_summary)

    def build_folders(self, structure, parent=None, level=0):
        """Recursively build folder structure."""
        for key, value in structure.items():
            # Create folder or item
            is_folder = isinstance(value, dict)
            self.add_item(key, is_folder, parent, level)

            # If it's a folder, recurse to add sub-items
            if is_folder:
                self.build_folders(value, key, level + 1)

    def add_item(self, name, is_folder, parent=None, level=0):
        """Add a folder or option item to the navigation system."""
        container = CTk.CTkFrame(self)
        container.pack(fill="x", padx=10 * level, pady=(2, 2))

        if is_folder:
            toggle_button = CTk.CTkButton(
                container,
                text=f"📁 {name}",
                anchor="w",
                command=lambda: self.toggle_folder(name),
                fg_color="transparent",
                text_color="blue",
            )
            toggle_button.pack(fill="x")
            self.folder_widgets[name] = {"button": toggle_button, "items": []}
        else:
            item_button = CTk.CTkButton(
                container,
                text=f"📄 {name}",
                anchor="w",
                command=lambda: self.callback(parent, name),
                fg_color="transparent",
                hover_color="lightblue",
            )
            item_button.pack(fill="x")

            if parent:
                self.folder_widgets[parent]["items"].append(container)

    def toggle_folder(self, folder_name):
        """Expand or collapse the contents of a folder."""
        folder_data = self.folder_widgets.get(folder_name)
        if not folder_data:
            return

        is_expanded = folder_data["items"][0].winfo_ismapped() if folder_data["items"] else False

        for item in folder_data["items"]:
            if is_expanded:
                item.pack_forget()  # Collapse
            else:
                item.pack(fill="x", padx=20, pady=2)  # Expand
                
                


class ParameterWidget(CTk.CTkFrame):
    def __init__(self, master, parameter_name, current_value, default_value, param_type, choices=None, **kwargs):
        super().__init__(master, corner_radius=10, border_width=1, border_color="#444", **kwargs)
        self.parameter_name = parameter_name
        self.current_value = current_value
        self.default_value = default_value
        self.param_type = param_type
        self.choices = choices

        # Convert class values to their names for display
        if isinstance(self.current_value, type):
            self.current_value = self.current_value.__name__
        if isinstance(self.default_value, type):
            self.default_value = self.default_value.__name__

        param_type_display = param_type.__name__ if isinstance(param_type, type) else str(param_type)

        # State management
        self.is_modified = self.current_value != self.default_value
        self.is_valid = True
        # Configure grid layout with tighter spacing
        self.grid_columnconfigure(0, minsize=180)  # Parameter name
        self.grid_columnconfigure(1, minsize=120)  # Type
        self.grid_columnconfigure(2, weight=1, minsize=160)  # Input
        self.grid_columnconfigure(3, minsize=80)  # Restore button
        self.grid_columnconfigure(4, minsize=90)  # Status
        self.grid_rowconfigure(0, weight=1)

        # Smaller fonts and tighter padding
        self.name_label = CTk.CTkLabel( self, text=parameter_name, font=("Segoe UI", 15))
        self.name_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")

        self.type_label = CTk.CTkLabel( self, text=param_type_display, font=("Segoe UI", 13))
        self.type_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Input field with constrained width
        self.value_input = self.create_input_field(self.current_value)
        self.value_input.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Compact restore button
        self.restore_button = CTk.CTkButton( self, text="Reset", width=60, height=28, command=self.restore_to_default, fg_color="#444", hover_color="#333", state="disabled", font=("Segoe UI", 13))
        self.restore_button.grid(row=0, column=3, padx=5, pady=5)

        # Status label with fixed width
        self.status_label = CTk.CTkLabel( self, text=self.get_status_text(), font=("Segoe UI", 13), text_color=self.get_status_color(), width=80, anchor="center")
        self.status_label.grid(row=0, column=4, padx=(5, 10), pady=5)

        # Set fixed frame height
        self.configure(height=36)  # Matches component heights
        self.restore_to_default()

    def create_input_field(self, value):
        """Create input field with constrained dimensions"""
        input_width = 250  # Reduced width

        if self.param_type == bool:
            switch = CTk.CTkSwitch(self, text="", command=self.validate_input, switch_width=60, switch_height=20)
            return switch
        elif self.param_type == int:
            spinbox = IntSpinbox(self, default_value=int(value), command=self.validate_input)
            return spinbox
        elif self.param_type == float:
            spinbox = FloatSpinbox(self, default_value=float(value), command=self.validate_input)
            return spinbox
        elif self.choices:
            dropdown = CTk.CTkComboBox(self, values=[c.__name__ for c in self.choices], command=self.validate_input, width=input_width, dropdown_font=("Segoe UI", 11), button_color="#444")
            return dropdown
        else:  # Entries for strings
            entry = CTk.CTkEntry(
                self,
                width=input_width,
                height=28,
                placeholder_text=str(value),
                font=("Segoe UI", 11)
            )
            entry.bind("<KeyRelease>", self.validate_input)
            entry.bind("<FocusOut>", self.validate_input)
            return entry

    def restore_to_default(self):
        """Reset parameter to default value."""
        if isinstance(self.value_input, CTk.CTkEntry):
            self.value_input.delete(0, "end")
            self.value_input.insert(0, str(self.default_value))
        elif isinstance(self.value_input, CTk.CTkSwitch):
            if bool(self.value_input.get()) != self.default_value:
                self.value_input.toggle()
        elif isinstance(self.value_input, Spinbox):
            self.value_input.set_value(self.default_value)
        self.validate_input()

    def validate_input(self, event=None):
        """Validate and update parameter state."""
        # Get raw input value
        if isinstance(self.value_input, CTk.CTkComboBox):
            raw_value = self.value_input.get()
        elif isinstance(self.value_input, CTk.CTkSwitch):
            raw_value = bool(self.value_input.get())
        else:
            raw_value = self.value_input.get()

        if self.param_type is None or isinstance(raw_value, self.param_type):
            self.is_valid = True
            self.current_value = raw_value
        else:
            self.is_valid = False

        self.is_modified = (self.is_valid and (self.current_value != self.default_value))

        self.update_status_label()

    def get_status_text(self):
        return "Invalid" if not self.is_valid else "Modified" if self.is_modified else "Default"

    def get_status_color(self):
        return "#ff4444" if not self.is_valid else "#4CAF50" if self.is_modified else "#888"

    def update_status_label(self):
        self.status_label.configure(text=self.get_status_text(), text_color=self.get_status_color())
        self.restore_button.configure(state="normal" if self.is_modified else "disabled")

    def get_value(self):
        """Return the current validated value or None if invalid."""
        return self.current_value if self.is_valid else None