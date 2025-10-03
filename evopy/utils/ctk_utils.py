import tkinter

import customtkinter as CTk
from typing import Union, Callable, Any, get_origin, get_args
from inspect import isclass
from math import inf

def type_to_str(_type) -> str:
    origin = get_origin(_type)
    args = get_args(_type)
    if isinstance(_type, type):
        return _type.__name__
    elif _type is Any:
        return "Any"
    elif origin is Union:
        args_set = set(args)
        if type(None) in args_set:
            args_set.remove(type(None))
            if len(args_set) == 1:
                return f"Optional[{type_to_str(args[0])}]"
        return " | ".join(map(type_to_str, args_set))
    elif origin is not None:
        origin_name = getattr(origin, "__name__", str(origin).replace("typing.", ""))
        if args:
            return f"{origin_name}[{', '.join(map(type_to_str, args))}]"
        else:
            return origin_name

    return str(_type).replace("typing.", "")

def to_str(obj) -> str:
    if isclass(obj):
        return type_to_str(obj)
    else:
        return str(obj)

def dict_to_str(d):
    def convert(v):
        if callable(v):
            return v.__name__  # on remplace la fonction par son nom
        elif isinstance(v, dict):
            return "{" + ', '.join(f'"{convert(k)}": {convert(vv)}' for k, vv in v.items()) + "}"
        else:
            return str(v)
    return convert(d)

def isinstance_or_subclass(obj_or_cls, tp) -> bool:
    """Return True if obj_or_cls is an instance of tp OR a subclass of tp."""
    origin = get_origin(tp)
    args = get_args(tp)

    # Handle Any
    if tp is Any:
        return True
    if tp is type and isinstance(obj_or_cls, type):
        return True
    check = issubclass if isinstance(obj_or_cls, type) else isinstance
    if origin is None:
        return check(obj_or_cls, tp)
    if origin is Union:
        return any(isinstance_or_subclass(obj_or_cls, arg) for arg in args)
    if not check(obj_or_cls, origin):
        return False
    if not args:
        return True
    # Only makes sense to validate args if we're checking an *instance*
    if not isinstance(obj_or_cls, type):
        if origin in (list, set, frozenset):
            elem_type = args[0]
            return all(isinstance_or_subclass(el, elem_type) for el in obj_or_cls)
        if origin is tuple:
            if len(args) == 2 and args[1] is Ellipsis:
                return all(isinstance_or_subclass(el, args[0]) for el in obj_or_cls)
            if len(obj_or_cls) != len(args):
                return False
            return all(isinstance_or_subclass(el, arg) for el, arg in zip(obj_or_cls, args))
        if origin is dict:
            key_type, val_type = args
            return all(
                isinstance_or_subclass(k, key_type) and
                isinstance_or_subclass(v, val_type)
                for k, v in obj_or_cls.items()
            )
    return True

def is_optional(tp):
    return get_origin(tp) is Union and type(None) in get_args(tp)



class Spinbox(CTk.CTkFrame):
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 step_size: Union[int, float] = 1,
                 default_value: Union[int, float] = 0,
                 command: Callable = None,
                 **kwargs):
        super().__init__(*args, width=width, height=height)

        self.step_size = step_size
        self.command = command

        self.configure(fg_color=("gray78", "gray28"))  # set frame color

        self.grid_columnconfigure((0, 2), weight=0)  # buttons don't expand
        self.grid_columnconfigure(1, weight=1)  # entry expands

        self.subtract_button = CTk.CTkButton(self, text="-", width=height-6, height=height-6,
                                                       command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.text = CTk.StringVar(value=str(default_value))
        self.entry = CTk.CTkEntry(self, width=width-(2*height), height=height-6, border_width=0, textvariable=self.text)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")
        self.entry.bind("<ButtonRelease-1>", self.command)
        self.text.trace_add("write", lambda *_: self.command())
        self.add_button = CTk.CTkButton(self, text="+", width=height-6, height=height-6,
                                                  command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        
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
            self.set(self.right_transform())
        except ValueError:
            pass
        if self.command is not None:
            self.command()

    def subtract_button_callback(self):
        try:
            self.set(self.left_transform())
        except ValueError:
            pass
        if self.command is not None:
            self.command()

    def set(self, value: Union[float, int]):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))
        


class IntSpinbox(Spinbox):
    
    def _get(self) -> int:
        return int(super()._get())
    
class FloatSpinbox(Spinbox):

    def __init__(self, *args, step_size=0.1, **kwargs) -> None:
        super().__init__(*args, step_size=step_size, **kwargs)
    
    def _get(self) -> float:
        return round(float(super()._get()), 5)
    
class BoundedSpinbox(Spinbox):
    
    def __init__(self, *args, width = 100, height = 32, step_size = 1, default_value = 0, command = None, min_value=-inf, max_value=inf, **kwargs):
        super().__init__(*args, width=width, height=height, step_size=step_size, default_value=default_value, command=command, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        
    def _left_transform(self) -> Union[float, int, None]:
        return max(self.min_value, self.get() - self.step_size)
    
    def _right_transform(self) -> Union[float, int, None]:
        return min(self.max_value, self.get() + self.step_size)

    def set(self, value: Union[float, int]):
        value = max(min(value, self.max_value), self.min_value)
        super().set(value)
    
class BoundedIntSpinbox(BoundedSpinbox, IntSpinbox):
    
    def __init__(self, *args, width=100, height=32, step_size=1, default_value=0, command=None, min_value=-inf, max_value=inf, **kwargs):
        super().__init__(*args, width=width, height=height, step_size=step_size, default_value=default_value, command=command, min_value=min_value, max_value=max_value, **kwargs)
    
class BoundedFloatSpinbox(BoundedSpinbox, FloatSpinbox):

    def __init__(self, *args, step_size=0.1, **kwargs):
        super().__init__(*args, step_size=step_size, **kwargs)
        
    
class BoolSwitch(CTk.CTkSwitch):

    def __init__(self, *args, default_value=False, onvalue=True, offvalue=False, **kwargs) -> None:
        super().__init__(*args, text="", switch_width=60, switch_height=20, onvalue=onvalue, offvalue=offvalue)
        self.set(default_value)

    def set(self, value: bool):
        if value:
            self.select()
        else:
            self.deselect()

class ChoicesBox(CTk.CTkComboBox):

    def __init__(self, *args, values=None, **kwargs) -> None:
        self.to_display = lambda x: to_str(x)
        self.values_dict = {to_str(v): v for v in values} | {"None": None}
        super().__init__(*args, values=list(map(self.to_display, values)),  width=250, button_color="#444", state="readonly")

    def get(self):
        return self.values_dict[super().get()]

    def set(self, value):
        super().set(to_str(value))

class StringEntry(CTk.CTkEntry):
    def __init__(self, *args, default_value=None, command=None, **kwargs) -> None:
        self.command = command
        self.text = CTk.StringVar(value=default_value)

        if self.command is not None:
            self.text.trace_add("write", lambda *_: self.command())

        super().__init__(*args, width=250, height=28,
                         textvariable=self.text, font=("Segoe UI", 11),
                         )

        self.bind("<Return>", lambda event: self.command() if self.command else None)

    def set(self, value: str):
        """Set the entry text programmatically."""
        self.text.set(value)

    def disable(self):
        self.configure(state="disabled", fg_color="gray30",  bg_color= "lightgray")

    def enable(self):
        self.configure(state="normal", fg_color="white", bg_color = "black")

    def switch(self):
        if self._state == "disabled":
            self.enable()
        else:
            self.disable()

class CodeEntry(CTk.CTkEntry):
    def __init__(self, *args, default_value=None, command=None, **kwargs) -> None:
        self.command = command
        print(dict_to_str(default_value))
        self.text = CTk.StringVar(value=dict_to_str(default_value))

        if self.command is not None:
            self.text.trace_add("write", lambda *_: self.command())

        super().__init__(*args, width=250, height=28,
                         textvariable=self.text, font=("Segoe UI", 11))

        self.bind("<Return>", lambda event: self.command() if self.command else None)

    def set(self, value: str):
        """Set the entry text programmatically."""
        self.text.set(dict_to_str(value))

    def get(self):
        """Get the entry text programmatically."""
        try:
            value = eval(self.text.get())
        except:
            value = None
        return value

class Optional:

    def __init__(self, value_entry):
        self.value_entry = value_entry

    def set(self, value):
        if value is None:
            self.disable()
        else:
            self.enable()
        self.value_entry.set(value)

    def disable(self):
        self.value_entry.grid_forget()

    def enable(self):
        self.value_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")


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
    def __init__(self, master, parameter_name, current_value, default_value, param_type, extra: dict, **kwargs):
        super().__init__(master, corner_radius=10, border_width=1, border_color="#444")
        self.parameter_name = parameter_name
        self.current_value = current_value
        self.default_value = default_value
        self.param_type = param_type
        #self.choices = choices
        self.is_optional = is_optional(parameter_name)
        self.visible: bool = current_value is not None

        if "choices" in extra and extra["choices"] is not None:
            self.value_input = ChoicesBox(self, values=extra["choices"], command=self.validate_input, **extra)
        elif self.param_type == int:
            spinbox = BoundedIntSpinbox if "min_value" in extra or "max_value" in extra else IntSpinbox
            self.value_input = spinbox(self, default_value=self.current_value, command=self.validate_input, **extra)
        elif self.param_type == float:
            spinbox = BoundedFloatSpinbox if "min_value" in extra or "max_value" in extra else FloatSpinbox
            self.value_input = spinbox(self, default_value=self.current_value, command=self.validate_input, **extra)
        elif self.param_type == bool:
            self.value_input = BoolSwitch(self, default_value=self.current_value, command=self.validate_input, **extra)
        elif self.param_type == str:
            self.value_input = StringEntry(self, default_value=self.current_value, command=self.validate_input, **extra)
        else:
            print(f"Invalid parameter type {self.param_type}")
            self.value_input = CodeEntry(self, default_value=self.current_value, command=self.validate_input, **extra)

        self.status = None

        self.grid_columnconfigure(0, minsize=180)  # Parameter name
        self.grid_columnconfigure(1, minsize=120)  # Type
        self.grid_columnconfigure(3, weight=1, minsize=160)  # Input
        self.grid_columnconfigure(4, minsize=80)  # Restore button
        self.grid_columnconfigure(5, minsize=90)  # Status
        self.grid_rowconfigure(0, weight=1)

        self.name_label = CTk.CTkLabel( self, text=parameter_name, font=("Segoe UI", 15))
        self.name_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")

        self.type_label = CTk.CTkLabel( self, text=type_to_str(self.param_type), font=("Segoe UI", 13))
        self.type_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        if is_optional(param_type):
            self.grid_columnconfigure(2, minsize=60)
            self.optional = BoolSwitch(self, default_value=False, command=lambda: self.switch_entry_visibility(), onvalue="normal", offvalue="disabled")
            self.optional.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.value_input.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.restore_button = CTk.CTkButton( self, text="Reset", width=60, height=28, command=self.restore_to_default, fg_color="#444", hover_color="#333", state="disabled", font=("Segoe UI", 13))
        self.restore_button.grid(row=0, column=4, padx=5, pady=5)

        self.status_label = CTk.CTkLabel( self, text=self.get_status_text(), font=("Segoe UI", 13), text_color=self.get_status_color(), width=80, anchor="center")
        self.status_label.grid(row=0, column=5, padx=(5, 10), pady=5)

        self.configure(height=36)
        self.restore_to_default()

    def switch_entry_visibility(self):
        if self.visible:
            self.visible = False
            self.value_input.grid_forget()
        else:
            self.visible = True
            self.value_input.grid(row=0, column=3, padx=5, pady=5, sticky="ew")


    def restore_to_default(self):
        """Reset parameter to default value."""
        self.value_input.set(self.default_value)
        self.validate_input()

    def validate_input(self, event=None):
        """Validate and update parameter state."""
        value = self.value_input.get()
        if self.param_type is None or isinstance_or_subclass(value, self.param_type): # Add validation in the value input to check with extras (ex int > 0)
            self.current_value = value
            self.status = "Modified" if self.current_value != self.default_value else "Default"
        else:
            self.status = "Invalid"
        self.update_status_label()

    def save_value(self):
        if self.status == "Modified":
            self.status = "Saved"
            self.update_status_label()
            return True
        return False

    def switch_off(self):
        if is_optional(self.param_type):
            return not self.optional.get()
        return False

    def get_status_text(self):
        return self.status

    def get_status_color(self):
        match self.status:
            case "Invalid":
                return "#ff4444"
            case "Modified":
                return "#4CAF50"
            case "Saved":
                return "#7DF9FF"
            case "Default":
                return "#888"

    def update_status_label(self):
        self.status_label.configure(text=self.get_status_text(), text_color=self.get_status_color())
        self.restore_button.configure(state="disabled" if self.status == "Default" else "normal")

    def get_value(self):
        """Return the current validated value or None if invalid."""
        return self.current_value if not self.status == "Invalid" else None