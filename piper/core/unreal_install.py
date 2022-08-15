#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import piper.config.unreal as ucfg


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
        raise ValueError(f'{project_path} does not exist! Please use valid .uproject path')

    project_directory = os.path.dirname(project_path)
    default_engine = os.path.join(project_directory, 'Config', 'DefaultEngine.ini')

    if os.path.exists(default_engine):
        return default_engine

    # make a DefaultEngine.ini file since it does not exist
    print(f'Creating {default_engine} since it was not found!')
    with open(default_engine, 'w') as _:
        pass

    return default_engine


def validatePythonDirectory(project_path):
    """
    Validates the python directory in the Unreal project's content directory.

    Args:
        project_path (string): Path to unreal project which includes all source code, ending in .uproject

    Returns:
        (string): Full path to the python directory in the project's content directory.
    """
    if not os.path.exists(project_path):
        raise ValueError(f'{project_path} does not exist! Please use valid .uproject path')

    project_directory = os.path.dirname(project_path)
    python_directory = os.path.join(project_directory, 'Content', 'Python')

    if os.path.exists(python_directory):
        return python_directory

    os.mkdir(python_directory)
    return python_directory


def defaultConfig(project_path, piper_directory):
    """
    Writes piper's init_unreal.py to the given project's DefaultEngine.ini config. This allows piper to be part of
    the python path on the given unreal project start up.

    Args:
        project_path (string): Path to unreal project which includes all source code, ending in .uproject

        piper_directory (string): Path to piper's main package folder. Usually same as os.environ['PIPER_DIR'].

    Examples:
        install('D:/Projects/UE5/Hawaii', 'D:/Projects/piper')
    """
    print('-' * 50)
    engine_config = validateEngineConfig(project_path)
    script_directory = os.path.join(piper_directory, 'unreal', 'scripts').replace('\\', '/')
    additional_line = ucfg.python_additional_key + script_directory + '")\n'
    piper_paragraph = ucfg.python_section + additional_line

    # Manually parsing .ini config file instead of using configparser library since unreal config files can have
    # duplicates of keys, which configparser does not do well with since configparser is a dictionary
    with open(engine_config, 'r') as open_file:
        data = open_file.readlines()

    # if the piper path is already in the config file, don't do anything
    if additional_line in data:
        print(f'Piper path already in {engine_config}')
        return

    # add the python config section to the data if it doesn't exists
    if ucfg.python_section not in data:
        print(f'Writing Piper path to {engine_config}')
        data.append(ucfg.python_section)

    # create a list with the python key value line and write it to the file
    lines = [piper_paragraph if ucfg.python_section in line else line for line in data]
    with open(engine_config, 'w') as open_file:
        open_file.writelines(lines)


def symlink(project_path, piper_directory):
    """
    Creates a symlink between the init_unreal.py and setup.py scripts in the piper directory and the Unreal project's
    python directory in the content folder.

    Args:
        project_path (string): Path to unreal project which includes all source code, ending in .uproject

        piper_directory (string): Path to piper's main package folder. Usually same as os.environ['PIPER_DIR'].
    """
    python_directory = validatePythonDirectory(project_path)
    target_init_unreal_script = os.path.join(python_directory, ucfg.init_unreal_name).replace('\\', '/')
    target_setup_script = os.path.join(python_directory, ucfg.setup_name).replace('\\', '/')

    script_directory = os.path.join(piper_directory, 'unreal', 'scripts')
    source_init_unreal_script = os.path.join(script_directory, ucfg.init_unreal_name).replace('\\', '/')
    source_setup_script = os.path.join(script_directory, ucfg.setup_name).replace('\\', '/')

    try:
        os.symlink(source_init_unreal_script, target_init_unreal_script)
        print(f'Linking {source_init_unreal_script} to {target_init_unreal_script}')

        os.symlink(source_setup_script, target_setup_script)
        print(f'Linking {source_setup_script} to {target_setup_script}')
    except OSError as error:
        print('WARNING: Run piper_installer.exe as administrator to symlink!')
        raise error
