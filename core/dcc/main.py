#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import winreg


class DCC(object):
    """
    Shell class to define behavior for getting information about digital content creation packages.
    """
    def __init__(self):
        """
        Public variables with None assigned MUST be overridden in child class.
        """
        # public variables
        self.name = type(self).__name__
        self.version_replace = 'VERSION_NAME'  # Used to later replace version.
        self.registry_path = None  # override. App dependent
        self.registry_exclude = None  # override. App dependent
        self.registry_install_key = None  # override. App dependent
        self.registry_install_path = None  # override. App dependent
        self.relative_python_path = None  # override. App dependent
        self.relative_batch_path = None  # override. App dependent

        # private variables
        self._install_directories = {}
        self._python_paths = {}
        self._batch_paths = {}
        self._versions = None

    def preValidateVersions(self):
        """
        Raises errors if class' values are not properly set.
        """
        if not self.registry_path:
            raise ValueError('Please set class\' registry path.')

        if not self.name:
            raise ValueError('Please set class\' name.')

    def getVersions(self):
        """
        Gets all the installed versions of the dcc.

        Returns:
            (set): Versions installed as strings.
        """
        if self._versions:
            return self._versions

        versions = set()
        self.preValidateVersions()
        access_registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        h_key = winreg.OpenKey(access_registry, self.registry_path)

        # if user has more than 20 versions installed, I will be impressed, and user has a problem.
        for key in range(20):
            try:
                version = winreg.EnumKey(h_key, key)

                if version != self.registry_exclude:
                    versions.add(str(version))

            except WindowsError:
                break

        self._versions = versions
        return versions

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
        Gets the install directory for the given version of the dcc.

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
        Gets all the install directories for all versions of the dcc.

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

    def preValidatePython(self):
        """
        Raises errors if class' values are not properly set.
        """
        if not self.relative_python_path:
            raise ValueError('Please set class\' relative python path.')

    def getPythonPath(self, version):
        """
        Gets the python executable for the given version.

        Args:
            version (string): Version to get the python executable of.

        Returns:
            (string): Path to python executable of dcc.
        """
        if version in self._python_paths:
            return self._python_paths[version]

        self.preValidatePython()
        install_directory = self.getInstallDirectory(version)
        python_path = self.relative_python_path.copy()
        python_path.insert(0, install_directory)
        python_path = os.path.join(*python_path)
        self._python_paths[version] = python_path
        return python_path

    def getPythonPaths(self):
        """
        Gets all the python paths available for all the versions of the dcc.

        Returns:
            (dictionary): Path as key, version as value.
        """
        python_paths = {}

        for version in self.getVersions():
            python_path = self.getPythonPath(version)
            python_paths[python_path] = version

        return python_paths

    def preValidateBatch(self):
        """
        Raises errors if class' values are not properly set.
        """
        if not self.relative_python_path:
            raise ValueError('Please set class\' relative batch path.')

    def getBatchPath(self, version):
        """
        Gets the path to the batch version of the dcc with the given version.

        Args:
            version (string): Version to get batch path of.

        Returns:
            (string): Path to batch executable.
        """
        if version in self._batch_paths:
            return self._batch_paths[version]

        self.preValidateBatch()
        install_directory = self.getInstallDirectory(version)
        batch_path = self.relative_batch_path.copy()
        batch_path.insert(0, install_directory)
        batch_path = os.path.join(*batch_path)
        self._batch_paths[version] = batch_path
        return batch_path

    def getBatchPaths(self):
        """
        Gets the batch paths to all the installed versions of the dcc.

        Returns:
            (dictionary): Batch path as key, version as value.
        """
        batch_paths = {}

        for version in self.getVersions():
            batch_path = self.getBatchPath(version)
            batch_paths[batch_path] = version

        return batch_paths

    def printInfo(self):
        """
        Prints all the information this class can gather.
        """
        versions = self.getVersions()
        install_directories = self.getInstallDirectories()
        python_paths = self.getPythonPaths()
        batch_paths = self.getBatchPaths()

        print('\n' + ('=' * 20))
        print('DCC: ' + self.name)

        print('\nVERSION(S): ')
        [print(version) for version in versions]

        print('\nINSTALL DIRECTORY(IES): ')
        [print(install_directory) for install_directory in install_directories]

        print('\nPYTHON PATH(S): ')
        [print(python_path) for python_path in python_paths]

        print('\nBATCH PATH(S): ')
        [print(batch_path) for batch_path in batch_paths]
