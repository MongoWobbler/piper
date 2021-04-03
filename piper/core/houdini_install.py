#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import sys
import json
import hou


environment_directory = sys.argv[1]
packages_directory = os.path.join(hou.getenv('HOUDINI_USER_PREF_DIR'), 'packages')
piper_package = os.path.join(packages_directory, 'piper.json')

if not os.path.exists(packages_directory):
    os.makedirs(packages_directory)

data = {
        "env": [{"PIPER_DIR": environment_directory}],
        "path": environment_directory + '/houdini'
        }

print('Writing environment to: {}'.format(piper_package))
with open(piper_package, 'w') as open_file:
    json.dump(data, open_file, indent=4)
