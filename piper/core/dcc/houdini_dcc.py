#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
from piper.core.dcc import DCC


class Houdini(DCC):

    def __init__(self):
        super(Houdini, self).__init__()
        self.registry_path = 'SOFTWARE\\Side Effects Software'
        self.registry_exclude = 'Houdini'
        self.registry_install_key = 'InstallPath'
        self.registry_install_path = 'SOFTWARE\\Side Effects Software\\{}'.format(self.version_replace)
        self.relative_python_path = ['bin', 'hython.exe']
        self.relative_batch_path = ['bin', 'houdini.exe']

    def onBeforeInstalling(self):
        os.environ['HOUDINI_NO_ENV_FILE'] = '1'
