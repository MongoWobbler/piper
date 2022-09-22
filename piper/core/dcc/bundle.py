#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import copy
import socket
import subprocess
import winreg

import piper.core.pather as pather


class DCC(object):
    """
    Semi-abstract class to define behavior for getting information about digital content creation packages.
    """
    def __init__(self):
        """
        Public variables with None assigned MUST be overridden in child class.
        """
        # public variables
        self.name = type(self).__name__
        self.address = None  # override. App dependent. Host and port to connect to.
        self.process_name = None  # override. App dependent
        self.registry_path = None  # override. App dependent
        self.registry_exclude = None  # override as list. App dependent
        self.registry_install_key = None  # override. App dependent
        self.registry_install_path = None  # override. App dependent
        self.relative_python_path = None  # override. App dependent
        self.relative_batch_path = None  # override. App dependent
        self.relative_process_path = None  # override. App dependent
        self.open_command = None  # override. App dependent. Command to send to DCC to open a path
        self.export_command = None  # override. App dependent. Command to export scene to game directory.

        # private variables
        self.version_replace = 'VERSION_NAME'  # Used to later replace version.
        self._install_directories = {}
        self._python_paths = {}
        self._batch_paths = {}
        self._process_paths = {}
        self._versions = None

    def preValidateVersions(self):
        """
        Raises errors if class' values are not properly set.
        """
        if not self.registry_path:
            raise ValueError('Please set class\' registry path.')

        if not self.name:
            raise ValueError('Please set class\' name.')

    def getVersions(self, error=False):
        """
        Gets all the installed versions of the dcc.

        Args:
            error (boolean): If True, will raise error if no versions are found.

        Returns:
            (set): Versions installed as strings.
        """
        if self._versions:
            return self._versions

        versions = set()
        self.preValidateVersions()
        access_registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

        # try to find registry path, if not found return empty or raise error
        try:
            h_key = winreg.OpenKey(access_registry, self.registry_path)
        except FileNotFoundError as error_message:
            if error:
                raise error_message
            else:
                self._versions = versions
                return versions

        # if user has more than 20 versions installed, I will be impressed, and user has a problem.
        for key in range(20):
            try:
                version = winreg.EnumKey(h_key, key)

                if version not in self.registry_exclude:
                    versions.add(str(version))

            except WindowsError:
                break

        self._versions = versions
        return versions

    def getLatestVersion(self):
        """
        Gets the latest version of the DCC found.

        Returns:
            (string): Latest version of the DCC found.
        """
        versions = self.getVersions(error=True)
        versions = list(versions)
        versions.sort(reverse=True)
        return versions[0]

    def isInstalled(self):
        """
        Gets whether the DCC is installed in the registry or not.

        Returns:
            (boolean): True if installed, false if not.
        """
        return True if self.getVersions() else False

    def preValidateInstall(self):
        """
        Raises errors if class' values are not properly set.
        """
        if not self.registry_install_path:
            raise ValueError('Please set class\' registry install path.')

        if not self.registry_install_key:
            raise ValueError('Please set class\' registry install key.')

    def getInstallDirectory(self, version):
        """
        Gets the installation directory for the given version of the dcc.

        Args:
            version (string): Version to get install directory of.

        Returns:
            (string): Path to directory where DCC is installed.
        """
        if version in self._install_directories:
            return self._install_directories[version]

        self.preValidateInstall()
        install_path = self.registry_install_path.replace(self.version_replace, version)
        h_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, install_path)
        directory, result = winreg.QueryValueEx(h_key, self.registry_install_key)
        self._install_directories[version] = directory
        return directory

    def getInstallDirectories(self, error=False):
        """
        Gets all the installation directories for all versions of the dcc.

        Args:
            error (boolean): If True, will raise error if version without install directory found.

        Returns:
            (dictionary): Install directory string as key, version string as value.
        """
        install_directories = {}

        for version in self.getVersions():
            try:
                directory = self.getInstallDirectory(version)
                install_directories[directory] = version
            except OSError as error_message:
                print(self.name + ' ' + version + ' does not have a install path.'
                                                  ' Check the Windows registry and/or re-install. ')
                if error:
                    raise error_message

        return install_directories

    def _getPath(self, version, validator, relative_path, paths):
        """
        Gets the executable for the given relative path for the given version.

        Args:
            version (string): Version to get the executable of.

            validator (method): Method used to validate variables are set correctly.

            relative_path (list): Path relative to install directory to find executable

            paths (dictionary): Used to cache found paths. Version as key, path as value.

        Returns:
            (string): Path to python executable of dcc.
        """
        if version in paths:
            return paths[version]

        validator()
        install_directory = self.getInstallDirectory(version)
        batch_path = copy.deepcopy(relative_path)
        batch_path.insert(0, install_directory)
        batch_path = os.path.join(*batch_path)
        paths[version] = batch_path
        return batch_path

    def _getPaths(self, getter):
        """
        Gets all the paths for the given getter available for all the versions of the dcc.

        Returns:
            (dictionary): Path as key, version as value.
        """
        paths = {}
        for version in self.getVersions():
            python_path = getter(version)
            paths[python_path] = version

        return paths

    def preValidatePython(self):
        """
        Raises errors if class' values are not properly set.
        """
        if not self.relative_python_path:
            raise ValueError('Please set class\' relative python path.')

    def preValidateBatch(self):
        """
        Raises errors if class' values are not properly set.
        """
        if not self.relative_batch_path:
            raise ValueError('Please set class\' relative batch path.')

    def preValidateProcess(self):
        """
        Raises errors if class' values are not properly set.
        """
        if not self.relative_process_path:
            raise ValueError('Please set class\' relative process path.')

    def getPythonPath(self, version):
        """
        Gets the python executable for the given version.

        Args:
            version (string): Version to get the python executable of.

        Returns:
            (string): Path to python executable of dcc.
        """
        return self._getPath(version, self.preValidatePython, self.relative_python_path, self._python_paths)

    def getBatchPath(self, version):
        """
        Gets the path to the batch version of the dcc with the given version.

        Args:
            version (string): Version to get batch path of.

        Returns:
            (string): Path to batch executable.
        """
        return self._getPath(version, self.preValidateBatch, self.relative_batch_path, self._batch_paths)

    def getProcessPath(self, version):
        """
        Gest the path to the process version of the dcc with the given version.

        Args:
            version (string): Version to get the regular executable path of.

        Returns:
            (string): Path to DCC executable.
        """
        return self._getPath(version, self.preValidateProcess, self.relative_process_path, self._process_paths)

    def getPythonPaths(self):
        """
        Gets all the python paths available for all the versions of the dcc.

        Returns:
            (dictionary): Path as key, version as value.
        """
        return self._getPaths(self.getPythonPath)

    def getBatchPaths(self):
        """
        Gets the batch paths to all the installed versions of the dcc.

        Returns:
            (dictionary): Batch path as key, version as value.
        """
        return self._getPaths(self.getBatchPath)

    def getProcessPaths(self):
        """
        Gets the process paths to all the installed versions of the dcc.

        Returns:
            (dictionary): Process path as key, version as value.
        """
        return self._getPaths(self.getProcessPath)

    def isRunning(self):
        """
        Gets whether the DCC is currently running. Uses the task manager command "TASKLIST" to find process.

        Returns:
            (boolean): True if DCC is running.
        """
        if not self.process_name:
            raise ValueError('Please set class\' process name.')

        command = 'TASKLIST /FI "imagename eq {}"'.format(self.process_name)
        output = subprocess.check_output(command).decode()
        data = output.strip().split('\r\n')[-1]
        return data.lower().startswith(self.process_name.lower())

    def launch(self, version, *args):
        """
        Launches the DCC of the given version.

        Args:
            version (string): DCC version to run.
        """
        path = self.getProcessPath(version)
        command = ['start', path] + list(args)
        return subprocess.run(command, universal_newlines=True, shell=True, check=True, capture_output=True)

    def launchLatest(self, *args):
        """
        Launches the latest version of the DCC installed.
        """
        version = self.getLatestVersion()
        return self.launch(version, *args)

    def send(self, command, display=True):
        """
        Sends the given command to the Digital Content Creation's address.

        Args:
            command (string): Command to execute in the DCC.

            display (boolean): If True, will print results from command that was executed in the DCC.

        Returns:
            (string): Results of command executed in DCC.
        """
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(self.address)
        client.send(command.encode())
        data = client.recv(1024).decode()
        client.close()

        if display and data and data != 'None\n\x00':
            print(data)

        return data

    def open(self, path, display=True):
        """
        Opens the given path in the DCC.

        Args:
            path (string): Path to open file in DCC.

            display (boolean): If True, will print results from command that was executed in DCC.

        Returns:
            (string): Results of command executed in DCC.
        """
        if self.isRunning():
            print(f'Opening {path} in a existing {self.name} process.')
            command = self.open_command.format(path)
            return self.send(command, display=display)
        else:
            print(f'Opening {path} in a new {self.name} process.')
            return self.launchLatest(path)

    def export(self, *args, **kwargs):
        """
        App dependent.
        """
        pass

    def onBeforeInstalling(self):
        """
        Useful for injecting environment keys before running installer.
        """
        pass

    def _runInstaller(self, python, install_script, install_directory):
        """
        Convenience method to log and run the python executable with the given install script.

        Args:
            python (string): Path to python executable for DCC.

            install_script (string): Full path to the python script the DCC is going to run to install
            environment variables.

            install_directory (string): Full path to directory that the given
            install_script will add to the environment.
        """
        print('-' * 50)
        print('Starting ' + self.name + '\'s ' + python)
        subprocess.run([python, install_script, install_directory], shell=True)

    def runInstaller(self, install_script, install_directory, versions=None, clean=False):
        """
        Runs the given install_script with the given install_directory passed to it on all versions of the DCC.

        Args:
            install_script (string): Full path to the python script the DCC is going to run to install
            environment variables.

            install_directory (string): Full path to directory that the given
            install_script will add to the environment.

            versions (string or list): Version(s) to install. If None given will attempt to install all versions.

            clean (boolean): If True, will delete all compiled (.pyc) scripts in the installation directory.
        """
        if not self.isInstalled():
            print(self.name + ' is not installed, skipping.')
            return

        if versions is None:
            self.printInfo()
            paths = self.getPythonPaths()
        elif isinstance(versions, str):
            paths = [self.getPythonPath(versions)]
        else:
            paths = [self.getPythonPath(version) for version in versions]

        if clean:
            pather.deleteCompiledScripts(install_directory)

        self.onBeforeInstalling()
        [self._runInstaller(python, install_script, install_directory) for python in paths]

    @staticmethod
    def _printInfo(text, iterables):
        """
        Convenience method for printing information about the dcc.

        Args:
            text (string): Text to display

            iterables (list or dictionary or set): Each item will be displayed.
        """
        print('\n' + text)
        [print(iterable) for iterable in iterables]

    def printInfo(self):
        """
        Prints all the information this class can gather.
        """
        versions = self.getVersions()
        install_directories = self.getInstallDirectories()
        python_paths = self.getPythonPaths()
        batch_paths = self.getBatchPaths()
        process_paths = self.getProcessPaths()

        print('\n' + ('=' * 50))
        print('DCC: ' + self.name)

        if self.isInstalled():
            self._printInfo('VERSION(S): ', versions)
            self._printInfo('INSTALL DIRECTORY(S): ', install_directories)
            self._printInfo('PYTHON PATH(S): ', python_paths)
            self._printInfo('BATCH PATH(S): ', batch_paths)
            self._printInfo('PROCESS PATH(S): ', process_paths)
        else:
            print('No versions found in registry. Is ' + self.name + ' installed?')

        print('\n')
