#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
import copy
import piper_config as pcfg
import piper.core.util as pcu


class Store(object):
    # turning store into a singleton
    instance = None

    def __init__(self):
        self._app_name = pcu.getApp()
        self._app = None
        self._version = ''
        self._path = None
        self._settings = {}
        self._default_settings = copy.deepcopy(pcfg.store_defaults)

    def getVersion(self):
        """
        App dependent.
        """
        pass

    def getApp(self):
        """
        Gets the app name with version attached to it.

        Returns:
            (string): Name of app currently running this script.
        """
        if self._app:
            return self._app

        if not self._version:
            self.getVersion()

        self._app = '_'.join([self._app_name, self._version]) if self._version else self._app_name
        return self._app

    def getPath(self):
        """
        Gets the path to the stored settings .json file.

        Returns:
            (string):
        """
        if self._path:
            return self._path

        piper_directory = pcu.getPiperDirectory()
        app = self.getApp()
        self._path = os.path.join(piper_directory, 'settings', app + '.json')
        return self._path

    def create(self, force=False):
        """
        Writes the defaults settings.

        Args:
            force (boolean): If True, will overwrite current settings with default.
        """
        if self._settings and not force:
            raise ValueError('Settings already exist! Please pass "force" as True to overwrite.')

        self._settings = copy.deepcopy(self._default_settings)
        pcu.writeJson(self.getPath(), self._settings)

    def getSettings(self):
        """
        Gets the stored settings. Will first attempt to get from memory, if nothing stored in memory,
        Then will read from disk and store what it read in the disk.

        Returns:
            (dictionary): Stored settings.
        """
        if self._settings:
            return self._settings

        settings_path = self.getPath()
        if os.path.exists(settings_path):
            self._settings = pcu.readJson(settings_path)
            return self._settings

        self.create()
        return self._settings

    def get(self, variable):
        """
        Gets the stored setting associated with the given variable.

        Args:
            variable (string): Name of setting to search for.

        Returns:
            (Any): Setting stored.
        """
        if not self._settings:
            self.getSettings()

        # updating settings when NEW default settings variables might not have been added
        # to existing settings .json file on disk
        if variable not in self._settings:
            self.set(variable, self._default_settings[variable])

        return self._settings[variable]

    def set(self, variable, value):
        """
        Sets and stores the given setting based on variable and value.

        Args:
            variable (string): Name of setting to store.

            value (Any): Value of given variable to store.
        """
        if not self._settings:
            self.getSettings()

        self._settings[variable] = value
        self.writeSettings()

    def update(self, data):
        """
        Updates the settings dictionary with the given data dictionary.

        Args:
            data (dictionary): Dictionary that adds to current settings.
        """
        if not self._settings:
            self.getSettings()

        self._settings.update(data)
        self.writeSettings()

    def writeSettings(self):
        """
        Convenience method for writing settings to disk file.
        """
        pcu.writeJson(self.getPath(), self._settings)


def get():
    """
    Gets the instance to the store since it is meant to be a singleton.
    """
    Store.instance = Store() if Store.instance is None else Store.instance
    return Store.instance
