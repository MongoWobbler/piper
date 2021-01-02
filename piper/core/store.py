#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import os
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

    def getVersion(self):
        """
        App dependent.
        """
        pass

    def getApp(self):
        if self._app:
            return self._app

        if not self._version:
            self.getVersion()

        self._app = '_'.join([self._app_name, self._version])
        return self._app

    def getPath(self):
        if self._path:
            return self._path

        piper_directory = pcu.getPiperDirectory()
        app = self.getApp()
        self._path = os.path.join(piper_directory, 'settings', app + '.json')
        return self._path

    def create(self, force=False):
        if self._settings and not force:
            return ValueError('Settings already exist! Please pass "force" as True to overwrite.')

        self._settings = {'art_directory': None,
                          'game_directory': None}

        pcu.writeJson(self.getPath(), self._settings)

    def getSettings(self):
        if self._settings:
            return self._settings

        settings_path = self.getPath()
        if os.path.exists(settings_path):
            self._settings = pcu.readJson(settings_path)
            return self._settings

        self.create()
        return self._settings

    def get(self, variable):
        if not self._settings:
            self.getSettings()

        return self._settings[variable]

    def set(self, variable, value):
        if not self._settings:
            self.getSettings()

        self._settings[variable] = value
        pcu.writeJson(self.getPath(), self._settings)


def get():
    Store.instance = Store() if Store.instance is None else Store.instance
    return Store.instance
