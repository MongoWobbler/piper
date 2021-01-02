#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

import pymel.core as pm
from piper.core.store import Store


class MayaStore(Store):

    instance = None

    def getVersion(self):
        if self._version:
            return self._version

        self._version = str(pm.about(version=True))
        return self._version


def enter():
    MayaStore.instance = MayaStore() if MayaStore.instance is None else MayaStore.instance
    return MayaStore.instance
