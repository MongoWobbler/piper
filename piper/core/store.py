#  Copyright (c) Christian Corsica. All Rights Reserved.

import os
import copy

import piper.core
import piper.config as pcfg
import piper.core.dcc as dcc
import piper.core.pythoner as python


class Store(object):
    # turning store into a singleton
    instance = None

    def __init__(self, app_name=None, defaults=pcfg.store_defaults):
        self._app_name = dcc.get() if app_name is None else app_name
        self._app = None
        self._version = ''
        self._path = None
        self._settings = {}
        self._default_settings = copy.deepcopy(defaults)

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

        piper_directory = piper.core.getPiperDirectory()
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
        python.writeJson(self.getPath(), self._settings)

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
            self._settings = python.readJson(settings_path)
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

    def getChecked(self, variable, error, description):
        """
        Gets the stored setting associated with the given variable and checks to make sure variable value is valid.
        If not valid, will raise given error with given description.

        Args:
            variable (string): Name of setting to search for.

            error (Error): Error to raise if value of setting is not valid.

            description (string): Text to raise for value being invalid.

        Returns:
            (Any): Setting stored.
        """
        variable = self.get(variable)

        if not variable:
            raise error(description)

        return variable

    def set(self, variable, value, write=True):
        """
        Sets and stores the given setting based on variable and value.

        Args:
            variable (string): Name of setting to store.

            value (Any): Value of given variable to store.

            write (boolean): If True, will write settings to file. Useful to turn off when setting multiple variables
            to avoid calling writing to file multiple times. If False, should call writeSettings after store.set()
        """
        if not self._settings:
            self.getSettings()

        self._settings[variable] = value

        if write:
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
        python.writeJson(self.getPath(), self._settings)


def get():
    """
    Gets the instance to the store since it is meant to be a singleton.
    """
    Store.instance = Store(app_name='Piper') if Store.instance is None else Store.instance
    return Store.instance


piper_store = get()
