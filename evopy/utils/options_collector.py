import os
import ast
from pathlib import Path

def extract_imports(file_path):
    """Extract all imports from the given file."""
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            tree = ast.parse(file.read(), filename=file_path)
        except SyntaxError:
            return {}

    imports = {}

    for node in ast.walk(tree):
        # Handle 'import module' or 'import module as alias'
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports[alias.asname or alias.name] = alias.name

        # Handle 'from module import name' or 'from module import name as alias'
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for alias in node.names:
                    imports[alias.asname or alias.name] = node.module

    return imports


def extract_options(file_path, imports, project_root):
    """
    Extract classes and detect the usage of `options.parameter` or `self._options.parameter`
    from a given Python file, including annotations if available.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            tree = ast.parse(file.read(), filename=file_path)
        except SyntaxError:
            return {}, set()

    file_structure = {}
    req_imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):  # Process each class definition
            class_name = node.name
            options_dict, required_imports = find_option_usages(node, imports, project_root)
            req_imports.update(required_imports)
            file_structure[class_name] = options_dict
                
    return file_structure, req_imports


def find_option_usages(class_node, imports, project_root):
    """
    Detect all occurrences of `options.parameter` or `self._options.parameter` within a class.
    If annotated assignments are found, include their types.
    """
    options_dict = {}
    req_imports = set()
    for node in ast.walk(class_node):
        # Handle annotated assignments specifically
        if isinstance(node, ast.AnnAssign) and isinstance(node.value, ast.Attribute):
            assign_options = isinstance(node.value.value, ast.Name) and node.value.value.id == "options"
            assign_self_options = (
                isinstance(node.value.value, ast.Attribute)
                and isinstance(node.value.value.value, ast.Name)
                and node.value.value.attr == "_options"
                and node.value.value.value.id == "self"
            )
            if assign_options or assign_self_options:
                annotation, required_imports = resolve_annotation(node.annotation, imports, project_root)
                options_dict[node.value.attr] = annotation
                req_imports.update(required_imports)

        # Check for `options.parameter` or `self._options.parameter` without assignment
        elif isinstance(node, ast.Attribute):
            find_option_1 = isinstance(node.value, ast.Name) and node.value.id == "options"
            find_option_2 = (
                isinstance(node.value, ast.Attribute)
                and isinstance(node.value.value, ast.Name)
                and node.value.value.id == "self"
                and node.value.attr == "_options"
            )
            if find_option_1 or find_option_2:
                options_dict.setdefault(node.attr, None)

    return options_dict, req_imports


def is_options_attribute(node, options_name):
    """
    Check if a node corresponds to `<options_name>.parameter` or `self.<options_name>.parameter`.
    """
    # Detect patterns like `options.parameter`
    if isinstance(node.value, ast.Name) and node.value.id == options_name:
        return True
    # Detect patterns like `self.<options_name>.parameter`
    if (
        isinstance(node.value, ast.Attribute)
        and isinstance(node.value.value, ast.Name)
        and node.value.value.id == "self"
        and node.value.attr == options_name
    ):
        return True

    return False



def resolve_annotation(annotation, imports, project_root):
    """Resolve the type annotation into a Python object or reference."""
    required_imports = set()

    # Handle classic built-in types
    builtin_types = {"int", "float", "str", "bool", "list", "dict", "tuple", "set", "type", "NoneType", "object", "None"}

    if isinstance(annotation, ast.Name):
        # Check if it's a built-in type
        if annotation.id in builtin_types:
            return annotation.id, required_imports
        elif annotation.id in imports:
            # Internal or external import
            module = imports[annotation.id]
            if module == "builtins":
                return annotation.id, required_imports
            else:
                return annotation.id, {f"from {module} import {annotation.id}"}

    elif isinstance(annotation, ast.Subscript):
        # Handle generic types like Union[float, int]
        if isinstance(annotation.value, ast.Name) and annotation.value.id == "Union":
            types = []
            for arg in annotation.slice.elts:
                resolved_type, sub_imports = resolve_annotation(arg, imports, project_root)
                types.append(resolved_type)
                required_imports.update(sub_imports)
            return " | ".join(types), required_imports

        elif isinstance(annotation.value, ast.Name):
            # Handle generic types like List[int]
            base_type, base_imports = resolve_annotation(annotation.value, imports, project_root)
            element_type, element_imports = resolve_annotation(annotation.slice, imports, project_root)
            required_imports.update(base_imports)
            required_imports.update(element_imports)
            return f"{base_type}[{element_type}]", required_imports

    return None, required_imports

def build_hierarchical_dict(base_dir, relative_path, project_structure, options_data):
    """Convert file structure into a hierarchical dictionary and embed options data."""
    parts = relative_path.split(os.sep)  # Split path into folders and file name
    current = project_structure

    for part in parts[:-1]:  # Traverse through folders
        current = current.setdefault(part, {})  # Ensure folder structure exists

    file_name = parts[-1]
    if file_name not in current:
        current[file_name] = {}  # Ensure file exists in the structure
    
    # Merge options_data with existing file data
    for class_name, class_options in options_data.items():
        current[file_name].setdefault(class_name, {}).update(class_options)

def collect_options_from_project(base_dir):
    """Walk through the project and collect all options and their types from classes."""
    project_structure = {}
    global_imports = set()

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                imports = extract_imports(file_path)
                file_options, file_imports = extract_options(file_path, imports, base_dir)
                if file_options:  # Only process files with detected options
                    relative_path = os.path.relpath(file_path, base_dir)
                    build_hierarchical_dict(base_dir, relative_path, project_structure, file_options)
                global_imports.update(file_imports)

    return project_structure, global_imports

def save_formatted_dict_to_file(dictionary, imports, file_path):
    """Save a well-formatted Python dictionary to a file."""
    with open(file_path, "w", encoding="utf-8") as file:
        # Write imports at the top of the file
        for imp in sorted(imports):
            file.write(f"{imp}\n")
        file.write("\noptions_summary = ")

        # Write the dictionary
        def write_nested_dict(d, indent=1):
            for key, value in d.items():
                file.write("    " * indent + f"{repr(key)}: ")
                if isinstance(value, dict):
                    file.write("{\n")
                    write_nested_dict(value, indent + 1)
                    file.write("    " * indent + "},\n")
                else:
                    file.write(f"{value},\n")

        file.write("{\n")
        write_nested_dict(dictionary)
        file.write("}\n")
        
def get_evopy_summary():
    current_dir = Path(__file__).resolve()
    project_path = current_dir.parent.parent
    options_data, global_imports = collect_options_from_project(str(project_path))
    return options_data, global_imports

if __name__ == "__main__":
    options_data, global_imports = get_evopy_summary()
    output_file = Path(__file__).resolve().parent.parent.parent / "options_summary.py"
    save_formatted_dict_to_file(options_data, global_imports, str(output_file))
    print("\nSaved formatted dictionary to 'options_summary.py'")
