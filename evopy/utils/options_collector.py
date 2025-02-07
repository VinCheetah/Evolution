import os
import ast
import importlib
import builtins
import importlib.util
import evopy
from pathlib import Path
from typing import Union, Callable, get_origin, get_args

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
            # Create relative path to the module from the project root
            options_dict, required_imports = find_option_usages(node, imports, project_root)
            req_imports.update(required_imports)
            module_name = file_path.replace('.py', '').replace('/', '.')
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            # Get the class from the module
            class_ = getattr(module, class_name)
            module_path = project_root.split("/")[-1] + "." + os.path.relpath(file_path, project_root).replace('.py', '').replace('/', '.')
            req_imports.add(f"from {module_path} import {class_.__name__}")
            
            file_structure[class_] = options_dict
                
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
            if is_options_attribute(node.value):
                annotation, required_imports = resolve_annotation(node.annotation, imports, project_root)
                options_dict[node.value.attr] = annotation
                req_imports.update(required_imports)

        # Check for `options.parameter` or `self._options.parameter` without assignment
        elif isinstance(node, ast.Attribute):
            if is_options_attribute(node):
                options_dict.setdefault(node.attr, None)

    return options_dict, req_imports


def is_options_attribute(node):
    """
    Check if the attribute node is an attribute of the options dictionary.
    """
    return (isinstance(node.value, ast.Name) and node.value.id == "options") or (
        isinstance(node.value, ast.Attribute) and isinstance(node.value.value, ast.Name)
        and node.value.attr == "_options" and node.value.value.id == "self"
    )


def resolve_annotation(annotation, imports, project_root):
    """Resolve the type annotation into a Python object or reference."""
    required_imports = set()

    if isinstance(annotation, ast.Name):
        # Check if it's a built-in type
        type_name = annotation.id
        if hasattr(builtins, type_name) and isinstance(getattr(builtins, type_name), type):
            return getattr(builtins, type_name), required_imports
        elif annotation.id in imports:
            module_name = imports[annotation.id]
            module = importlib.import_module(module_name)
    
            if hasattr(module, type_name):
                type_class = getattr(module, type_name)
            else:
                raise AttributeError(f"Type '{type_name}' not found in module '{module_name}'.")
            if module == "builtins":
                return type_class, required_imports
            else:
                return type_class, {f"from {module_name} import {type_name}"}
        else:
            raise AttributeError    

    elif isinstance(annotation, ast.Subscript):
        if isinstance(annotation.value, ast.Name):
            types = []
            base_type, base_imports = resolve_annotation(annotation.value, imports, project_root)
            # Handle different cases 
            if annotation.slice.__class__.__name__ == "Index":
                for node in annotation.slice.value.elts:
                    if isinstance(node, ast.Name):
                        type_, required_imports = resolve_annotation(node, imports, project_root)
                        types.append(type_)
                        required_imports.update(base_imports)
                    elif isinstance(node, ast.Str):
                        types.append(node.s)
                    elif isinstance(node, ast.Num):
                        types.append(node.n)
            else:
                type_, required_imports = resolve_annotation(annotation.slice, imports, project_root)
                types.append(type_)
                required_imports.update(base_imports)
            required_imports.update(base_imports)
            types = tuple(types) if len(types) > 1 else types[0]
            return base_type[types], required_imports
    return None, required_imports

def build_hierarchical_dict(base_dir, relative_path, project_structure, options_data):
    """Convert file structure into a hierarchical dictionary and embed options data."""
    parts = relative_path.split(os.sep)  # Split path into folders and file name
    current = project_structure

    #for part in parts[:-1]:  # Traverse through folders
    #    current = current.setdefault(part, {})  # Ensure folder structure exists
    current = current.setdefault(parts[0], {})

    
    # Merge options_data with existing file data
    for class_name, class_options in options_data.items():
        current.setdefault(class_name, {}).update(class_options)

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
                origin = get_origin(value)
                if isinstance(key, type):
                    file.write("    " * indent + f"{key.__name__}: ")
                else:
                    file.write("    " * indent + f"{repr(key)}: ")
                    
                if origin is not None and origin.__module__ in ["typing", "collections.abc"]:
                    file.write(f"{clean_typing_prefix(value)},\n")
                elif isinstance(value, type):
                    file.write(f"{value.__name__},\n")
                elif isinstance(value, dict):
                    file.write("{\n")
                    write_nested_dict(value, indent + 1)
                    file.write("    " * indent + "},\n")
                else:
                    file.write(f"{value},\n")

        file.write("{\n")
        write_nested_dict(dictionary)
        file.write("}\n")
        
def clean_typing_prefix(typ):
    """
    Generate a string representation of a type without 'typing.' prefixes,
    keeping 'Optional' intact and properly handling 'Callable'.

    Args:
        typ: The type to process.

    Returns:
        str: The cleaned string representation of the type.
    """
    origin = get_origin(typ)
    args = get_args(typ)

    # Handle Optional explicitly
    if origin is Union and type(None) in args:
        non_none_args = [arg for arg in args if arg is not type(None)]
        return f"Optional[{clean_typing_prefix(non_none_args[0])}]"

    # Handle Callable explicitly
    if origin is Callable:
        if args:
            # Split Callable arguments and return type
            arg_types = args[0]
            return_type = args[1]
            if isinstance(arg_types, tuple):
                arg_str = ", ".join(clean_typing_prefix(arg) for arg in arg_types)
            else:
                arg_str = clean_typing_prefix(arg_types)
            return f"Callable[[{arg_str}], {clean_typing_prefix(return_type)}]"
        return "Callable"

    if origin:
        # Handle generic types (e.g., List[int], Dict[str, int])
        origin_name = origin.__name__ if hasattr(origin, '__name__') else str(origin)
        if args:
            args_str = ", ".join(clean_typing_prefix(arg) for arg in args)
            return f"{origin_name}[{args_str}]"
        return origin_name
    elif hasattr(typ, '__name__'):
        # Handle non-generic types
        return typ.__name__
    else:
        # Handle literals and special cases
        return str(typ)
        
def get_evopy_summary():
    current_dir = Path(__file__).resolve()
    project_path = current_dir.parent.parent
    options_data, global_imports = collect_options_from_project(str(project_path))
    return options_data, global_imports

if __name__ == "__main__":
    import pprint
    options_data, global_imports = get_evopy_summary()
    output_file = Path(__file__).resolve().parent.parent.parent / "options_summary.py"
    save_formatted_dict_to_file(options_data, global_imports, str(output_file))
    print("\nSaved formatted dictionary to 'options_summary.py'")
    pprint.pprint(options_data)