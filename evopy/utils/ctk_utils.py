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
        if self.command is not None:
            self.command()
        try:
            self.set_value(self.right_transform())
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            self.set_value(self.left_transform())
        except ValueError:
            return

    def set_value(self, value: Union[float, int]):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))
        
        

class IntSpinbox(Spinbox):
    
    def _get(self) -> int:
        return int(super()._get())
    
class FloatSpinbox(Spinbox):
    
    def _get(self) -> float:
        return float(super()._get())
    
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
    pass
        
    



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
        """
        Initialize a ParameterWidget for a specific parameter.

        Args:
            master (tk.Widget): The parent widget.
            parameter_name (str): The name of the parameter.
            current_value: The current value of the parameter.
            default_value: The default value of the parameter.
            param_type (type): The expected type of the parameter.
            choices (list, optional): If the parameter has specific choices, provide them.
        """
        super().__init__(master, corner_radius=10, **kwargs)
        self.parameter_name = parameter_name
        self.current_value = current_value
        self.default_value = default_value
        self.param_type = param_type
        self.choices = choices

        # State
        self.is_modified = self.current_value != self.default_value
        self.is_valid = True

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # Name Label
        self.name_label = CTk.CTkLabel(self, text=parameter_name, font=("Arial", 14))
        self.name_label.grid(row=0, column=0, sticky="w", padx=10)

        # Type Label
        self.type_label = CTk.CTkLabel(self, text=f"Type: {param_type}", font=("Arial", 12), text_color="gray")
        self.type_label.grid(row=0, column=1, sticky="w", padx=10)

        # Value Input
        self.value_input = self.create_input_field(current_value)
        self.value_input.grid(row=0, column=2, padx=10)

        # Restore Button
        self.restore_button = CTk.CTkButton(
            self,
            text="Restore",
            width=80,
            command=self.restore_to_default,
            fg_color="gray",
            hover_color="darkgray",
        )
        self.restore_button.grid(row=0, column=3, padx=10)

        # Status Label
        self.status_label = CTk.CTkLabel(
            self,
            text=self.get_status_text(),
            font=("Arial", 12),
            text_color=self.get_status_color(),
        )
        self.status_label.grid(row=0, column=4, padx=10)

    def create_input_field(self, value):
        """
        Create an input field tailored to the parameter's type.

        Args:
            value: The current value of the parameter.

        Returns:
            CTk.Widget: A custom widget for the parameter's input.
        """
        if self.param_type == bool:
            # Boolean: Use a toggle switch
            toggle = CTk.CTkSwitch(self, text="", variable=CTk.IntVar(value=int(value)))
            toggle.bind("<ButtonRelease-1>", self.validate_input)
            return toggle
        elif self.param_type in [int, float, str]:
            # Number or String: Use an entry field
            entry = CTk.CTkEntry(self, placeholder_text=str(value))
            entry.bind("<FocusOut>", self.validate_input)
            return entry
        elif self.choices:
            # If choices are provided, use a dropdown
            dropdown = CTk.CTkComboBox(self, values=self.choices, command=self.validate_input)
            dropdown.set(str(value))
            return dropdown
        else:
            # Fallback: Use an entry field
            entry = CTk.CTkEntry(self, placeholder_text=str(value))
            entry.bind("<FocusOut>", self.validate_input)
            return entry

    def restore_to_default(self):
        """Restore the parameter to its default value."""
        self.current_value = self.default_value
        if isinstance(self.value_input, CTk.CTkEntry):
            self.value_input.delete(0, "end")
            self.value_input.insert(0, str(self.default_value))
        elif isinstance(self.value_input, CTk.CTkSwitch):
            self.value_input.set(int(self.default_value))
        elif isinstance(self.value_input, CTk.CTkComboBox):
            self.value_input.set(str(self.default_value))

        # Validate and update the UI
        self.is_modified = False
        self.is_valid = True
        self.update_status_label()

    def get_status_text(self):
        """Get the status text for the parameter."""
        if not self.is_valid:
            return "Invalid Type"
        return "Modified" if self.is_modified else "Default"

    def get_status_color(self):
        """Get the status color based on the parameter's state."""
        if not self.is_valid:
            return "red"
        return "green" if self.is_modified else "gray"

    def validate_input(self, event=None):
        """Validate the current value and update the UI."""
        input_value = (
            self.value_input.get()
            if isinstance(self.value_input, (CTk.CTkEntry, CTk.CTkComboBox))
            else self.value_input.get() == 1
        )

        # Type check
        try:
            if self.param_type in [int, float]:
                converted_value = self.param_type(input_value)
            elif self.param_type == bool:
                converted_value = bool(input_value)
            else:
                converted_value = input_value  # Assume valid for strings or unsupported types

            self.is_valid = True
            self.current_value = converted_value
        except (ValueError, TypeError):
            self.is_valid = False

        # Modification check
        self.is_modified = self.is_valid and (self.current_value != self.default_value)

        # Update UI
        self.update_status_label()

    def update_status_label(self):
        """Update the status label."""
        self.status_label.configure(
            text=self.get_status_text(),
            text_color=self.get_status_color(),
        )