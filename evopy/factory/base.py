from evopy.utils.default_options import default_opts
from evopy.utils.options_collector import get_evopy_summary
from evopy.utils.docstring_collector import get_evopy_summary as get_evopy_docstring
from evopy.utils.evo_types import Unknown
from evopy.utils.options import Options
from evopy.component import BaseComponent
from typing import Optional, Union, Callable


class BaseFactory(BaseComponent):
    """
    Base class for factory components

    Attributes:
        options (dict): Current options dictionary
        options_summary (dict): Options utilities for components
        options_default (dict): Options default dictionary
        components (list): List of components
        components_classes (dict[str, list[object]]): Dictionary of components for each type
        string_comp (dict[str, object]): Dictionary of composent names and their objects

    """
    def __init__(self, options_default: Optional[Options] = default_opts, extra_components: Optional[list] = None):
        BaseComponent.__init__(self, options_default)
        self.extra_components = extra_components if extra_components is not None else []
        # Initialize the options dictionary with metadata
        self.options_default = options_default
        self.options_summary_, _ = get_evopy_summary()
        self.options_summary = get_evopy_docstring()
        self.options: dict = {}
        self.components_classes: dict[str, list[type]] = {}
        self.components: list[type] = []
        self.string_comp: dict[str, type] = {}
        self._init_components()
        
    def _init_components(self):
        """
        Find all components of a given class name in the options summary.
        """
        self.components_classes = {component_type: list(components.keys()) for component_type, components in self.options_summary.items()}
        for component_type, components in self.options_summary.items():
            for component in components:
                if isinstance(component, type):
                    self.components.append(component)
                    self.string_comp[component.__name__] = component

    def check_parameters(self):
        missing_default = 0
        missing_summary = 0
        for key in self.options_default.keys():
            if not self._recursive_exist(self.options_summary, key):
                print(f"Parameter {key} not found in options summary")
                missing_summary += 1
        for key in self._get_recursive_keys(self.options_summary):
            if key not in self.options_default:
                print(f"Parameter {key} not found in default options")
                missing_default += 1
        if missing_default == missing_summary == 0:
            print("All parameters found in options summary and default options")
        else:
            print(f"Missing {missing_default} parameters in default options and {missing_summary} in options summary")

    def get_bases(self, comp_class) -> list[object | type]:
        """
        Get all base classes (direct and indirect) of a class.
        
        Args:
            comp_class (type | object): The class whose base classes need to be found.
            
        Returns:
            list: A list of all base classes.
        """
        base_classes = list(comp_class.__bases__)
        for base in comp_class.__bases__:
            base_classes.extend(self.get_bases(base))
        if object in base_classes:
            base_classes.remove(object)
        base_classes = [self.string_comp[base_class.__name__] for base_class in base_classes if base_class.__name__ in self.string_comp]
        return base_classes

    def get_component_summary(self, component: str):
        component_class = self.string_comp[component]
        for components_dict in self.options_summary.values():
            if component_class in components_dict:
                return components_dict[component_class]
        print(f"Component {component} not found in options summary")

    def _recursive_find(self, structure: dict, key, find_dict: bool = True):
        """
        Recursively search for a key in the options summary structure.
        """
        print(structure)
        if key in structure and (not find_dict ^ isinstance(structure[key], dict)):
            return structure[key]
        for value in structure.values():
            if isinstance(value, dict):
                result = self._recursive_find(value, key, find_dict)
                if result is not None:
                    return result
        return None
    
    def _recursive_exist(self, structure: dict, key):
        """
        Recursively search for a key in the options summary structure.
        """
        if key in structure:
            return True
        for value in structure.values():
            if isinstance(value, dict):
                if self._recursive_exist(value, key):
                    return True
        return False

    def _get_recursive_keys(self, structure: dict) -> list[str]:
        """
        Recursively collect all keys (parameters) from a given summary structure.
        """
        keys = []
        for sub_key, sub_structure in structure.items():
            if isinstance(sub_structure, dict):
                keys.extend(self._get_recursive_keys(sub_structure))
            else:
                keys.append(sub_key)
        return keys

    def get_default_value(self, key: str):
        """
        Retrieve the default value for a given option key.
        """
        return self.options_default.get(key)

    def get_option_type(self, key: str) -> type:
        """
        Retrieve the type of specific option recursively from the summary.
        """
        no_type_msg = f"Missing type for option '{key}'"
        param = self._recursive_find(self.options_summary, key, find_dict=True)
        if param is None or "type" not in param:
            self.log("warning", no_type_msg)
            exit(0)
        else:
            return self.str_to_type(param["type"])

    def str_to_type(self, str_type):
        if str_type in self.string_comp:
            return self.string_comp[str_type]
        return eval(str_type)

    def get_evopy_components(self) -> list[str]:
        """
        Returns the list of evopy components that the user should use.
        """
        unused_components = [] #["utils", "factory"]
        return [comp_type for comp_type in self.components_classes.keys() if comp_type not in unused_components]

    def validate_option(self, key: str, value):
        """
        Validate if the value matches the expected type from the summary.
        """
        expected_type = self.get_option_type(key)
        if expected_type is None:
            raise ValueError(f"Unknown option key: {key}")
        if expected_type is not None and not isinstance(value, expected_type):
            raise TypeError(f"Invalid type for key '{key}'. Expected {expected_type}, got {type(value)}.")

    def set_option(self, key, value):
        """
        Set an option value after validation.
        """
        self.validate_option(key, value)
        self.options[key] = value

    def get_option(self, key):
        """
        Retrieve the value of an option, defaulting to the default options if not explicitly set.
        """
        return self.options.get(key, self.get_default_value(key))

    def get_description(self, key):
        """
        Retrieve the description of an option, defaulting to the default options if not explicitly set.
        """
        no_description_msg = f"Missing description for option '{key}'"
        param = self._recursive_find(self.options_summary, key, find_dict=True)
        if param is None or "description" not in param:
            self.log("warning", no_description_msg)
            return no_description_msg
        else:
            return param["description"]

    def update_options(self, updates):
        """
        Bulk update options with validation.
        """
        for key, value in updates.items():
            self.set_option(key, value)

    def reset_option(self, key):
        """
        Reset an option to its default value.
        """
        default_value = self.get_default_value(key)
        if default_value is not None:
            self.options[key] = default_value
        elif key in self.options:
            del self.options[key]

    def reset_all_options(self):
        """
        Reset all options to their default values.
        """
        self.options.clear()

    def list_options(self):
        """
        List all current option settings.
        """
        return {key: self.get_option(key) for key in self.options_default.keys()}

    def get_choices(self, component_type):
        """
        Get the available choices for a given component type.
        """
        return [comp for comp in self.components if issubclass(comp, component_type)]

    def list_modified_options(self):
        """
        List all options that have been modified from their default values.
        """
        return {key: value for key, value in self.options.items() if key in self.options_default}

    def get_parameters_for_class(self, class_name) -> dict[str, dict]:
        """
        Retrieve all parameters for a given class from the summary.
        """
        class_summary = self.get_component_summary(class_name)
        if not isinstance(class_summary, dict):
            raise ValueError(f"No parameters found for class: {class_name}")
        return class_summary
        
    def get_all_parameters(self, component_name: str) -> list[tuple[str, dict[str, dict]]]:
        """
        Retrieve all parameters from the summary.
        """
        component_class = self.string_comp[component_name]
        parameters: list[tuple[str, dict]] = list()
        seen_parameters = set()
        for component in self.get_bases(component_class)[::-1] + [component_class]:
            if component in self.components:
                params = self.get_parameters_for_class(component.__name__)
                trash = set()
                for param in params.keys():
                    if param in seen_parameters:
                        seen_parameters.add(param)
                        trash.add(param)
                for param in trash:
                    del params[param]
                if len(params) > 0:
                    parameters.append((component.__name__, params))
        return parameters[::-1]

    def is_valid_parameter(self, parameter, parameter_name):
        parameter_type = self.get_option_type(parameter_name)
        if isinstance(parameter_type, list):
            return any([map(lambda param_type: self.is_valid_parameter(parameter, param_type), parameter_type)])
        else:
            return self.is_valid_parameter(parameter, parameter_name)

    @staticmethod
    def is_valid_type(parameter, parameter_type: type):
        if parameter_type is None:
            raise ValueError(f"Invalid parameter type '{parameter_type}'")
        return parameter_type == Unknown or isinstance(parameter, parameter_type)

    def save_options(self, file_path):
        """Save options to a file."""
        print(f"Options saved to {file_path} (not really saved).")

    def load_options(self, file_path):
        """Load options from a file."""
        print(f"Options loaded from {file_path} (not really loaded).")


    def describe_option(self, key):
        """
        Provide a description of an option including its default value, type, and current value.
        """
        return {
            "key": key,
            "default_value": self.get_default_value(key),
            "type": self.get_option_type(key),
            "current_value": self.get_option(key),
            "description": self.get_description(key),
        }


if __name__ == "__main__":
    factory = BaseFactory()
    print(factory.get_parameters_for_class("BaseMutator"))