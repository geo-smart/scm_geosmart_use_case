import ast
import importlib
import os

def extract_functions(node):
    if isinstance(node, ast.FunctionDef):
        return [node.name]
    return [f for child in ast.iter_child_nodes(node) for f in extract_functions(child)]

def check_function_existence(function_name):
    try:
        importlib.import_module('__main__').__dict__[function_name]
        return True
    except (ImportError, KeyError):
        return False

def collect_missing_functions(file_path):
    with open(file_path, 'r', encoding='utf-8') as notebook_file:
        notebook_content = notebook_file.read()

    notebook_ast = ast.parse(notebook_content)
    functions_used = extract_functions(notebook_ast)

    missing_functions = [func for func in functions_used if not check_function_existence(func)]
    return missing_functions

def traverse_notebooks(folder_path):
    missing_functions_all = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.ipynb'):
                file_path = os.path.join(root, file)
                missing_functions = collect_missing_functions(file_path)
                if missing_functions:
                    missing_functions_all.append((file_path, missing_functions))

    return missing_functions_all


def check_reproducibility_of_all_notebooks_in_a_folder(folder_path: str):
    # Specify the folder path to traverse
    folder_path = folder_path

    # Traverse notebooks and collect missing functions
    result = traverse_notebooks(folder_path)

    # Output missing functions, if any
    if result:
        error_msg = ""
        for file_path, missing_functions in result:
            error_msg += f"File: {file_path}\nMissing Functions: {', '.join(missing_functions)}\n"
        raise ValueError(error_msg)
    else:
        print("No missing functions found.")


check_reproducibility_of_all_notebooks_in_a_folder("./book/chapters")
