#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import piper.config as pcfg
import piper.config.houdini as hcfg
from piper.core.dcc.bundle import DCC


class Houdini(DCC):

    def __init__(self):
        super(Houdini, self).__init__()
        self.name = pcfg.houdini_name
        self.address = hcfg.address
        self.process_name = 'houdini.exe'
        self.registry_path = 'SOFTWARE\\Side Effects Software'
        self.registry_exclude = ['Houdini', 'Houdini Launcher']
        self.registry_install_key = 'InstallPath'
        self.registry_install_path = 'SOFTWARE\\Side Effects Software\\{}'.format(self.version_replace)
        self.relative_python_path = ['bin', 'hython.exe']
        self.relative_batch_path = ['bin', self.process_name]
        self.relative_process_path = ['bin', self.process_name]

    def onBeforeInstalling(self):
        os.environ['HOUDINI_NO_ENV_FILE'] = '1'
