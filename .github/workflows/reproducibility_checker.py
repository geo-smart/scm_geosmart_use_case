import ast
import importlib
import nbformat
import os

def extract_functions_from_notebook(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as notebook_file:
        notebook_content = nbformat.read(notebook_file, as_version=4)

    functions_called = set()

    for cell in notebook_content['cells']:
        if cell['cell_type'] == 'code':
            code_lines = cell['source'].split('\n')
            for line in code_lines:
                if line.strip().startswith(('def ', 'async def ')):
                    # Extracting function name from definition
                    function_name = line.split('(')[0].split(' ')[-1].strip()
                    functions_called.add(function_name)
                elif '(' in line and line.strip().endswith(')'):
                    # Extracting function name from function call
                    function_name = line.split('(')[0].strip()
                    functions_called.add(function_name)

    return functions_called

def check_functions_existence(functions, conda_env):
    missing_functions = [func for func in functions if not check_function_existence(func, conda_env)]
    return missing_functions

def check_function_existence(function_name, conda_env):
    try:
        importlib.import_module(conda_env).__dict__[function_name]
        return True
    except (ImportError, KeyError):
        return False

def traverse_notebooks(folder_path, conda_env):
    functions_called_all = {}

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.ipynb'):
                file_path = os.path.join(root, file)
                functions_called = extract_functions_from_notebook(file_path)
                missing_functions = check_functions_existence(functions_called, conda_env)
                if missing_functions:
                    functions_called_all[file_path] = missing_functions

    return functions_called_all


def check_reproducibility_of_all_notebooks_in_a_folder(folder_path: str):
    print(f"Checking the home directory: {folder_path}")
    # Specify the folder path to traverse
    folder_path = folder_path

    # Traverse notebooks and collect missing functions
    result = traverse_notebooks(folder_path, "geosmart")

    # Output missing functions, if any
    if result:
        error_msg = ""
        for file_path, missing_functions in result.items():
            error_msg += f"File: {file_path}\nMissing Functions: {', '.join(missing_functions)}\n"
        raise ValueError(error_msg)
    else:
        print("No missing functions found.")


check_reproducibility_of_all_notebooks_in_a_folder("./book/chapters")
