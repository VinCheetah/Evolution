import os
import ast
import importlib
import sys
from pathlib import Path
from typing import Dict, Any, Set


def extract_imports(file_path: str, project_root: str) -> Dict[str, str]:
    """Extrait les imports avec résolution correcte des chemins relatifs"""
    imports = {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            tree = ast.parse(file.read(), filename=file_path)
    except (SyntaxError, UnicodeDecodeError):
        return imports

    relative_path = os.path.relpath(os.path.dirname(file_path), project_root)
    package_parts = []
    if relative_path != ".":
        package_parts = relative_path.split(os.sep)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            level = node.level

            # Résolution des imports relatifs
            if level > 0:
                base_parts = package_parts[:-(level - 1)] if level > 1 else package_parts
                full_module = ".".join(base_parts + module.split("."))
            else:
                full_module = module

            for alias in node.names:
                key = alias.asname or alias.name
                imports[key] = f"{full_module}.{alias.name}" if full_module else alias.name

        elif isinstance(node, ast.Import):
            for alias in node.names:
                key = alias.asname or alias.name
                imports[key] = alias.name

    return imports


def process_file(file_path: str, project_root: str) -> Dict[str, Dict[str, Any]]:
    """Traite un fichier avec gestion améliorée des imports"""
    imports = extract_imports(file_path, project_root)

    with open(file_path, "r", encoding="utf-8") as file:
        try:
            tree = ast.parse(file.read())
        except SyntaxError:
            return {}

    results = {}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            class_info = analyze_options_usage(node)  # Fonction maintenant disponible
            if class_info:
                # Construction du chemin du module relatif au projet
                rel_path = os.path.relpath(file_path, project_root)
                module_path = rel_path.replace('/', '.').replace('\\', '.').rstrip('.py')

                # Ajout temporaire au path Python
                with add_to_syspath(project_root):
                    try:
                        module = importlib.import_module(module_path)
                        cls = getattr(module, node.name)
                        resolved_info = resolve_types(class_info, imports, project_root)
                        results[cls.__name__] = resolved_info
                    except (ImportError, AttributeError) as e:
                        print(f"Warning: Could not import {module_path}: {e}")

    return results

class OptionsUsageAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.attributes: Dict[str, Any] = {}
        self.function_calls: Set[str] = set()

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if self._is_options_attribute(target):
                attr_name = target.attr
                self.attributes[attr_name] = None

        if isinstance(node.value, ast.Call):
            if self._is_options_attribute(node.value.func):
                attr_name = node.value.func.attr
                self.function_calls.add(attr_name)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if self._is_options_attribute(node.target):
            attr_name = node.target.attr
            self.attributes[attr_name] = self._resolve_annotation(node.annotation)

    def visit_Call(self, node: ast.Call) -> None:
        if self._is_options_attribute(node.func):
            attr_name = node.func.attr
            self.function_calls.add(attr_name)

    def _is_options_attribute(self, node: ast.AST) -> bool:
        return (isinstance(node, ast.Attribute) and
                isinstance(node.value, (ast.Name, ast.Attribute)) and
                ((isinstance(node.value, ast.Name) and node.value.id == "options") or
                 (isinstance(node.value, ast.Attribute) and
                  node.value.attr == "_options" and
                  isinstance(node.value.value, ast.Name) and
                  node.value.value.id == "self")))

    def _resolve_annotation(self, annotation: ast.AST) -> str:
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            return f"{self._resolve_annotation(annotation.value)}[{self._resolve_annotation(annotation.slice)}]"
        return "Any"

    def get_filtered_attributes(self) -> Dict[str, Any]:
        return {k: v for k, v in self.attributes.items() if k not in self.function_calls}

# Ajout de la fonction manquante
def analyze_options_usage(class_node: ast.ClassDef) -> Dict[str, Any]:
    """Analyse l'utilisation des options dans une classe"""
    analyzer = OptionsUsageAnalyzer()
    analyzer.visit(class_node)
    return analyzer.get_filtered_attributes()

class add_to_syspath:
    """Context manager pour l'ajout temporaire au path système"""

    def __init__(self, path: str):
        self.path = path
        self.original_syspath = None

    def __enter__(self):
        self.original_syspath = sys.path.copy()
        if self.path not in sys.path:
            sys.path.insert(0, self.path)

    def __exit__(self, *args):
        sys.path = self.original_syspath


def resolve_types(class_info: Dict[str, Any], imports: Dict[str, str], project_root: str) -> Dict[str, Any]:
    """Résolution des types avec gestion des erreurs"""
    resolved = {}
    for attr, type_name in class_info.items():
        if type_name:
            try:
                if '.' in type_name:
                    module_part, _, class_part = type_name.rpartition('.')
                    with add_to_syspath(project_root):
                        module = importlib.import_module(module_part)
                        resolved_type = getattr(module, class_part)
                else:
                    resolved_type = getattr(__builtins__, type_name, None)
                    if not resolved_type:
                        resolved_type = imports.get(type_name, None)

                resolved[attr] = resolved_type.__name__ if resolved_type else None
            except Exception as e:
                print(f"Type resolution error for {type_name}: {e}")
                resolved[attr] = None
        else:
            resolved[attr] = None
    return resolved


def build_structure(project_root: str) -> Dict[str, Any]:
    """Construit la structure hiérarchique avec gestion des packages"""
    structure = {}
    project_root_path = Path(project_root)

    for root, dirs, files in os.walk(project_root):
        current_rel = Path(root).relative_to(project_root_path)
        current = structure

        for part in current_rel.parts:
            current = current.setdefault(part, {})

        for file in files:
            if file.endswith('.py') and file != '__init__.py':
                file_path = Path(root) / file
                classes = process_file(str(file_path), project_root)
                if classes:
                    current[file] = classes

    return structure


if __name__ == "__main__":
    # Chemin absolu du répertoire racine du projet
    project_root = str(Path(__file__).resolve().parent.parent)

    # Construction de la structure
    structure = build_structure(project_root)

    # Sauvegarde du résultat
    output_path = Path(__file__).resolve().parent.parent / 'options_summary.py'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('options_summary = ')
        f.write(repr(structure).replace("'", '"'))