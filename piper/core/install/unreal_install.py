#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import piper.config.unreal as ucfg
import piper.core.dcc.unreal_dcc as ue_dcc


def getScriptsDirectory(piper_directory):
    """
    Gets the path that holds the unreal python startup/setup scripts for piper.

    Args:
        piper_directory (string): Path to piper's main package folder. Usually same as os.environ['PIPER_DIR'].

    Returns:
        (string): Path to directory that holds init_unreal.py and setup.py in piper.
    """
    return os.path.join(piper_directory, ucfg.scripts_path).replace('\\', '/')


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
    engine_config = ue_dcc.validateEngineConfig(project_path)
    script_directory = getScriptsDirectory(piper_directory)
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


def validateSymlinkPath(directory, name):
    """
    Validates the path created by joining the given directory and name as a valid symlink path.

    Args:
        directory (string): Directory where symlink will be made to, the target.

        name (string): Name of target file.

    Returns:
        (string): Full path validated to make sure it does not already exist.
    """
    path = os.path.join(directory, name).replace('\\', '/')

    if os.path.islink(path):
        print(f'{path} link already exists! Removing...')
        os.remove(path)

    if os.path.exists(path):
        message = f'{path} already exists! Please specify another python path or manually remove file.'
        raise FileExistsError(message)

    return path


def symlink(piper_directory, project_path=None, target_directory=None):
    """
    Creates a symlink between the init_unreal.py and setup.py scripts in the piper directory and the Unreal project's
    python directory in the content folder.

    Args:
        project_path (string): Path to unreal project which includes all source code, ending in .uproject

        piper_directory (string): Path to piper's main package folder. Usually same as os.environ['PIPER_DIR'].

        target_directory (string): Path to where symlink will end up at. If None given, will use unreal
        project's Content/Python directory.
    """
    if not target_directory:
        target_directory = ue_dcc.validatePythonDirectory(project_path)

    script_directory = getScriptsDirectory(piper_directory)
    source_init_unreal_script = os.path.join(script_directory, ucfg.init_unreal_name).replace('\\', '/')
    source_setup_script = os.path.join(script_directory, ucfg.setup_name).replace('\\', '/')

    target_init_unreal_script = validateSymlinkPath(target_directory, ucfg.init_unreal_name)
    target_setup_script = validateSymlinkPath(target_directory, ucfg.setup_name)

    try:
        os.symlink(source_init_unreal_script, target_init_unreal_script)
        print(f'Linking {source_init_unreal_script} to {target_init_unreal_script}')

        os.symlink(source_setup_script, target_setup_script)
        print(f'Linking {source_setup_script} to {target_setup_script}')
    except OSError as error:
        print('WARNING: Run piper_installer.exe as administrator to symlink!')
        raise error
