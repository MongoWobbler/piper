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


def runInstaller(project_path, piper_directory):
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
