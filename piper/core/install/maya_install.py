#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import sys
import maya.cmds as mc
import maya.standalone
maya.standalone.initialize()


# global variables to define your own environment
MODULE_NAME = 'PIPER'
ENVIRONMENT_KEY = 'PIPER_DIR'
ENVIRONMENT = ['MAYA_ENABLE_LEGACY_VIEWPORT=1',
               'MAYA_NO_WARNING_FOR_MISSING_DEFAULT_RENDERER=1']

# directory to add to environment should be passed to this script as an argument
if len(sys.argv) < 2:
    raise IndexError('No directory specified. Please pass a directory to add to module to environment.')

# using maya's environment to figure out where to save modules to
environment_directory = sys.argv[1]
version = mc.about(version=True)
maya_directory = os.path.normpath(os.path.join(os.environ['MAYA_APP_DIR'], version))
modules_directory = os.path.normpath(os.path.join(maya_directory, 'modules'))

if not os.path.exists(modules_directory):
    os.makedirs(modules_directory)

# formatting lines for modules file.
lines = [f'+ {MODULE_NAME} 1.0 {environment_directory}/maya',
         f'{ENVIRONMENT_KEY}={environment_directory}',
         f'MAYA_CONTENT_PATH+={environment_directory}/maya/scenes',
         f'MAYA_PLUG_IN_PATH+={environment_directory}/maya/plug-ins/{version}']

lines += ENVIRONMENT
lines = [line + '\n' for line in lines]
modules_path = os.path.normpath(os.path.join(modules_directory, MODULE_NAME.lower() + '.mod'))
print(f'Writing environment to: {modules_path}')

with open(modules_path, 'w') as module_file:
    module_file.writelines(lines)

print(f'MAYA_APP_DIR = {maya_directory}')
