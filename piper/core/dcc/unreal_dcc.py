#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import subprocess
import piper.core.filer as filer


def validateEngineConfig(project_path):
    """
    Validates that a Config/DefaultEngine.ini file exists in the given project directory.
    If Config/DefaultEngine.ini file does not exist, creates a new empty DefaultEngine.ini file.

    Args:
        project_path (string): Path to unreal project which includes all source code, ending in .uproject

    Returns:
        (string): Full path to the DefaultEngine.ini of the given project.
    """
    if not os.path.exists(project_path):
        raise FileNotFoundError(f'{project_path} does not exist! Please use valid .uproject path')

    project_directory = os.path.dirname(project_path)
    default_engine = os.path.join(project_directory, 'Config', 'DefaultEngine.ini')

    if os.path.exists(default_engine):
        return default_engine

    # make a DefaultEngine.ini file since it does not exist
    print(f'Creating {default_engine} since it was not found!')
    with open(default_engine, 'w') as _:
        pass

    return default_engine


def validateLog(project_path, error=True):
    """
    Gets the latest log from the given project path.

    Args:
        project_path (string): Path to unreal project which includes all source code, ending in .uproject
        error (bool): If True, will raise FileNotFoundError if log is not found.

    Returns:
        (string): Full path to the latest log file for given project.
    """
    if not os.path.exists(project_path):
        raise FileNotFoundError(f'{project_path} does not exist! Please use valid .uproject path')

    project_name = os.path.basename(os.path.splitext(project_path)[0])
    project_directory = os.path.dirname(project_path)
    log = os.path.join(project_directory, 'Saved', 'Logs', project_name + '.log')

    if error and not os.path.exists(log):
        raise FileNotFoundError(f'{log} + does not exist!')

    return log


def getPythonPaths(editor_path, project_path):
    """
    Runs the given unreal editor with the given project path and prints all the paths in `sys.path`

    Args:
        editor_path (string): Path to unreal editor, if built: /UnrealEngine/Engine/Binaries/Win64/UnrealEditor.exe

        project_path (string): Path to unreal project which includes all source code, ending in .uproject
    """
    if not editor_path:
        raise FileNotFoundError('No Editor path was given! Please specify editor to check for python path.')

    if not os.path.exists(editor_path):
        raise FileNotFoundError(f'{editor_path} is not a real path! Please verify path exists.')

    if not project_path:
        raise FileNotFoundError('No project path was given! Please specify project to check for python path.')

    if not os.path.exists(project_path):
        raise FileNotFoundError(f'{project_path} is not a real path! Please verify path exists.')

    print('\n')
    message = 'jqz5piper'  # jqz are the least common letters, final message needs to be short to keep string together
    start = f"print('{message}')"
    end = f'LogPython: {message}'
    script = f'\\nimport sys\\nfor path in sys.path:\\n\\tprint(path)\\n{start}'
    command = f'"{editor_path}" "{project_path}" -run=pythonscript -script="{script}"'
    subprocess.run(command, shell=False)

    log = validateLog(project_path)
    return filer.pickText(log, start, end, start_exclude='LogPython: ')


def printPythonPaths(editor_paths, project_paths):
    """
    Prints the python paths from the linked lists of editor_paths and project_paths:

    Args:
        editor_paths (list): Paths to unreal engine editor to find python paths from.

        project_paths (list): Paths to unreal engine .uproject file to start editor with.
    """
    [print(path) for editor, project in zip(editor_paths, project_paths) for path in getPythonPaths(editor, project)]
