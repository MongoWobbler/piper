#  Copyright (c) Christian Corsica. All Rights Reserved.

import pymel.core as pm
import piper.config.maya as mcfg
from piper.core.store import Store


class MayaStore(Store):

    instance = None

    def getVersion(self):
        """
        Gets the current version of Maya as a string.

        Returns:
            (string): Version number
        """
        if self._version:
            return self._version

        self._version = str(pm.about(version=True))
        return self._version


def create():
    """
    Creates the store, only one instance can exist, making it a singleton.

    Returns:
        (MayaStore): Stores variables that can persist through application sessions.
    """
    MayaStore.instance = MayaStore(defaults=mcfg.store_defaults) if MayaStore.instance is None else MayaStore.instance
    return MayaStore.instance


maya_store = create()
