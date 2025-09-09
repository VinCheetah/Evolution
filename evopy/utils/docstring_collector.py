import os
import sys
import ast
import re
from importlib import import_module
from typing import Dict, Any

from evopy.component import BaseComponent
from evopy.utils.evo_types import Unknown
from pathlib import Path

bin_folder = ["utils", "factory", "__pycache__"]

def parse_parameters(docstring: str) -> Dict[str, Dict[str, Any]]:
    parameters = {}
    if not docstring:
        return parameters

    lines = [line for line in docstring.split('\n')]
    in_parameters = False
    current_param = None
    param_lines = []

    for line in lines:
        if line.lower().startswith('parameters:'):
            in_parameters = True
            continue
        elif in_parameters and not (line.lower().startswith('    ') or line == ""):
            in_parameters = False

        if not in_parameters:
            continue

        line = line.strip()
        # Updated regex to handle asterisk parameters
        param_match = re.match(r'^\*\s*(\w+)\s*(?:\(([^)]+)\))?\s*:\s*(.*)', line)
        if param_match:
            if current_param:
                process_param(current_param, param_lines, parameters)
            current_param = param_match.group(1)
            param_type = param_match.group(2) or None
            param_lines = [{
                'type': param_type,
                'content': param_match.group(3).strip()
            }]
        elif current_param and line:
            param_lines.append({'type': None, 'content': line.strip()})

    if current_param and param_lines:
        process_param(current_param, param_lines, parameters)

    return parameters


def process_param(name: str, lines: list, parameters: dict):
    param_info = {'parameter': True, 'type': Unknown, 'description': '', 'extras': {}}
    description_parts = []

    for line in lines:
        if line['type'] is not None:
            types = line['type'].split(' | ')
            param_info['type'] = types[0] if len(types) == 1 else types
        content = line['content']

        # Handle key-value pairs and standalone keys
        kv_match = re.match(r'^([A-Z][a-zA-Z]*)(?::\s*(.*))?$', content)
        if kv_match:
            key = kv_match.group(1).lower()
            value = kv_match.group(2).strip().rstrip('.') if kv_match.group(2) else True
            param_info['extras'][key] = value
        else:
            description_parts.append(content)

    param_info['description'] = ' '.join(description_parts).strip()
    parameters[name] = {k: v for k, v in param_info.items() if v or k == 'type'}


def analyze_component(path: str, module, root_path) -> Dict[str, Any]:
    component_dict = {}
    for root, mid, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read())
                    except SyntaxError:
                        continue

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            docstring = ast.get_docstring(node)
                            params = parse_parameters(docstring or '')
                            try:
                                comp_module = import_module(f"{module}")
                                comp_class = getattr(comp_module, node.name)
                            except AttributeError:
                                try:
                                    rel_folder = os.path.relpath(file_path, root_path).split(os.sep)
                                    rel_folder[-1] = rel_folder[-1][:-3]
                                    comp_module = import_module(f"{module}.{'.'.join(rel_folder[1:])}")
                                    comp_class = getattr(comp_module, node.name)
                                    print(f"Warning: could not import {node.name} directly from {module}")
                                except ModuleNotFoundError:
                                    print(f"Error: could not import {node.name} from {module}")
                                    continue
                            if issubclass(comp_class, BaseComponent):
                                component_dict[comp_class] = params
    return component_dict


def build_project_structure(root_path: str) -> Dict[str, Any]:
    structure = {}
    if str(root_path) not in sys.path:
        sys.path.append(str(root_path))
    module_name = os.path.basename(root_path)
    for entry in os.listdir(root_path):
        entry_path = os.path.join(root_path, entry)
        if os.path.isdir(entry_path) and entry not in bin_folder:
            sys.path.append(str(entry_path))  # Ensure Python can find the module
            component_dict = analyze_component(entry_path, f"{module_name}.{entry}", root_path)
            if component_dict:
                structure[entry] = component_dict
    return structure

def get_evopy_summary():
    current_dir = Path(__file__).resolve()
    evopy_path = current_dir.parent.parent
    options_data = build_project_structure(str(evopy_path))
    return options_data

if __name__ == '__main__':
    import pprint
    result = get_evopy_summary()
    pprint.pprint(result, width=180)