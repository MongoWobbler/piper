#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import subprocess
import piper.config as pcfg
import piper.config.maya as mcfg
import piper.core.pather as pather
import piper.core.vendor as vendor
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
        self.package_directory = 'scripts/site-packages'
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
        full_command = f'{batch_path} -noAutoloadPlugins -command "python(""{command}"")"'
        output = subprocess.run(full_command, capture_output=True, text=True)

        if display:
            print('\n', output.stdout)

    def runPythonBatches(self, command, display=True):
        [self.runPythonBatch(version, command, display) for version in self.getVersions()]

    def export(self, source_path, piper_node, source_method, version=None):
        command = self.export_command.format(source_path, piper_node, source_method)
        self.runPythonBatch(command, version=version)

    def exportFromJSON(self, json_file, version=None):
        command = self.export_from_json_command.format(json_file)
        self.runPythonBatch(command, version=version)

    def onBeforeInstalling(self):
        os.environ["PYTHONUNBUFFERED"] = "1"
        os.environ['MAYA_SKIP_USERSETUP_PY'] = '1'
        os.environ['PYMEL_SKIP_MEL_INIT'] = '1'

    def _runInstaller(self, python, version, install_script, install_directory):
        """
        Installing required pip packages to user's maya/scripts/site-packages.

        Args:
            python (string): Path to python executable for DCC.

            version (string): DCC version.

            install_script (string): Full path to the python script the DCC is going to run to install
            environment variables.

            install_directory (string): Full path to directory that the given
            install_script will add to the environment.

        Returns:
            (subprocess.CompletedProcess): Struct class containing completed process, such as stdout amd stderr.
        """
        # stdout from writing mod file includes the user's maya app directory.
        result = super(Maya, self)._runInstaller(python, version, install_script, install_directory)

        if not result:
            return None

        maya_directory = result.stdout.split("MAYA_APP_DIR = ")[-1].strip()
        target_directory = os.path.normpath(os.path.join(maya_directory, self.package_directory))
        pather.validateDirectory(target_directory)
        pip_command = [python, '-m', 'pip', 'install']

        [subprocess.run(pip_command + [package['name'], '--upgrade', '--target', target_directory])
         for package in pcfg.packages_to_install[self.name] if vendor.isValid(package, version)]

        return result
