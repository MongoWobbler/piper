#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import subprocess
from piper.core.dcc import DCC


class Maya(DCC):

    def __init__(self):
        super(Maya, self).__init__()
        self.process_name = 'maya.exe'
        self.registry_path = 'SOFTWARE\\Autodesk\\Maya'
        self.registry_exclude = ['Capabilities']
        self.registry_install_key = 'MAYA_INSTALL_LOCATION'
        self.registry_install_path = 'SOFTWARE\\Autodesk\\Maya\\{}\\Setup\\InstallPath'.format(self.version_replace)
        self.relative_python_path = ['bin', 'mayapy.exe']
        self.relative_batch_path = ['bin', 'mayabatch.exe']
        self.relative_process_path = ['bin', self.process_name]

    def runPythonBatch(self, version, command):
        batch_path = self.getBatchPath(version)
        full_command = '{0} -noAutoloadPlugins -command "python(""{1}"")"'.format(batch_path, command)
        subprocess.call(full_command)

    def runPythonBatches(self, command):
        for version in self.getVersions():
            self.runPythonBatch(version, command)

    def onBeforeInstalling(self):
        os.environ['MAYA_SKIP_USERSETUP_PY'] = '1'
        os.environ['PYMEL_SKIP_MEL_INIT'] = '1'
