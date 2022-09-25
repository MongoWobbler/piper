#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import subprocess
import piper.config as pcfg
import piper.config.maya as mcfg
from piper.core.dcc.bundle import DCC


class Maya(DCC):

    def __init__(self):
        super(Maya, self).__init__()
        self.name = pcfg.maya_name
        self.address = mcfg.address
        self.process_name = 'maya.exe'
        self.registry_path = 'SOFTWARE\\Autodesk\\Maya'
        self.registry_exclude = ['Capabilities']
        self.registry_install_key = 'MAYA_INSTALL_LOCATION'
        self.registry_install_path = 'SOFTWARE\\Autodesk\\Maya\\{}\\Setup\\InstallPath'.format(self.version_replace)
        self.relative_python_path = ['bin', 'mayapy.exe']
        self.relative_batch_path = ['bin', 'mayabatch.exe']
        self.relative_process_path = ['bin', self.process_name]
        self.open_command = "import pymel.core as pm; import piper.mayapy.ui.window as uiwindow; None if " \
                            "uiwindow.save() else pm.error('Maya scene was not saved.'); pm.openFile(r'{}', f=True) "
        self.export_command = "import pymel.core as pm; import setup; setup.piperTools(is_headless=True); " \
                              "pm.openFile(r'{0}', f=True); pm.select('{1}'); {2} "
        self.export_from_json_command = "import setup; setup.piperTools(is_headless=True); " \
                                        "import piper.mayapy.pipe.export; piper.mayapy.pipe.export.fromJSON('{0}')"

    def runPythonBatch(self, command, version=None, display=True):
        if not version:
            version = self.getLatestVersion()

        batch_path = self.getBatchPath(version)
        full_command = '{0} -noAutoloadPlugins -command "python(""{1}"")"'.format(batch_path, command)
        output = subprocess.run(full_command, capture_output=True)

        if display:
            print('\n', output.stdout.decode('utf-8'))

    def runPythonBatches(self, command, display=True):
        [self.runPythonBatch(version, command, display) for version in self.getVersions()]

    def export(self, source_path, piper_node, source_method, version=None):
        command = self.export_command.format(source_path, piper_node, source_method)
        self.runPythonBatch(command, version=version)

    def exportFromJSON(self, json_file, version=None):
        command = self.export_from_json_command.format(json_file)
        self.runPythonBatch(command, version=version)

    def onBeforeInstalling(self):
        os.environ['MAYA_SKIP_USERSETUP_PY'] = '1'
        os.environ['PYMEL_SKIP_MEL_INIT'] = '1'
