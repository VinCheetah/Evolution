from evopy.component import BaseComponent
from evopy.utils.default_options import default_opts
from evopy.utils.options_collector import get_evopy_summary
import evopy
import pprint


class BaseFactory(BaseComponent):

    def __init__(self):
        # Initialize the options dictionary with metadata
        self.options_default = default_opts
        self.options_summary, _ = get_evopy_summary()
        self.options = {}
        self.components_types: list["str"] = []
        self.components: list[object] = []
        self.components_parameters: dict[str, list[object]] = {}
        self._init_components()

        
    def _init_components(self):
        """
        Find all components of a given class name in the options summary.
        """
        for component_name, file_data in self.options_summary.items():
            self.components_types.append(component_name)
            self.components_parameters[component_name] = []
            self._find_components(component_name, file_data)
    
    def get_bases(self, comp_class) -> list[object]:
        """
        Get all base classes (direct and indirect) of a class.
        
        Args:
            cls (type): The class whose base classes need to be found.
            
        Returns:
            list: A list of all base classes.
        """
        base_classes = list(comp_class.__bases__)
        for base in comp_class.__bases__:
            base_classes.extend(self.get_bases(base))
        return base_classes


    def _find_components(self, comp_name, structure, is_file=False):
        """
        Recursively search for components in the options summary structure.
        """
        for key, value in structure.items():
            if isinstance(value, dict):
                if is_file:
                    try:
                        comp = eval(".".join(["evopy", comp_name, key]))
                        self.components.append(comp)
                        self.components_parameters[comp_name].append(comp)
                    except AttributeError:
                        pass
                else:
                    self._find_components(comp_name, value, is_file=(".py" in key))
                    
    def check_parameters(self):
        errors = 0
        for key in self.options_default.keys():
            if not self._recursive_exist(self.options_summary, key):
                print(f"Parameter {key} not found in options summary")
                errors += 1
        if errors == 0:
            print("All parameters found in options summary")
        else:
            print(f"{errors} errors found in options summary")

    def _recursive_find(self, structure, key):
        """
        Recursively search for a key in the options summary structure.
        """
        if key in structure:
            return structure[key]
        for value in structure.values():
            if isinstance(value, dict):
                result = self._recursive_find(value, key)
                if result is not None:
                    return result
        return None
    
    def _recursive_exist(self, structure, key):
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

    def _recursive_collect_keys(self, structure):
        """
        Recursively collect all keys (parameters) from a given summary structure.
        """
        keys = []
        for sub_key, sub_structure in structure.items():
            if isinstance(sub_structure, dict):
                keys.extend(self._recursive_collect_keys(sub_structure))
            else:
                keys.append(sub_key)
        return keys

    def get_default_value(self, key):
        """
        Retrieve the default value for a given option key.
        """
        return self.options_default.get(key, None)

    def get_option_type(self, key):
        """
        Retrieve the type of a specific option recursively from the summary.
        """
        return self._recursive_find(self.options_summary, key)

    def validate_option(self, key, value):
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
    
    def list_modified_options(self):
        """
        List all options that have been modified from their default values.
        """
        return {key: value for key, value in self.options.items() if key in self.options_default}

    def get_parameters_for_class(self, class_name):
        """
        Retrieve all parameters for a given class from the summary.
        """
        class_summary = self._recursive_find(self.options_summary, class_name)
        if not isinstance(class_summary, dict):
            raise ValueError(f"No parameters found for class: {class_name}")
        return list(class_summary.keys())
        
    def get_all_parameters(self, component_class):
        """
        Retrieve all parameters from the summary.
        """
        parameters = list()
        seen_parameters = set()
        for component in self.get_bases(component_class)[::-1] + [component_class]:
            if component in self.components:
                params = list()
                for param in self.get_parameters_for_class(component.__name__):
                    if param not in seen_parameters:
                        params.append(param)
                        seen_parameters.add(param)
                parameters.append((component.__name__, params))
        return parameters[::-1]


    def describe_option(self, key):
        """
        Provide a description of an option including its default value, type, and current value.
        """
        return {
            "key": key,
            "default_value": self.get_default_value(key),
            "type": self.get_option_type(key),
            "current_value": self.get_option(key)
        }
