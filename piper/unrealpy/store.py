#  Copyright (c) Christian Corsica. All Rights Reserved.

import unreal as ue
import piper.config.unreal as ucfg
from piper.core.store import Store


class UnrealStore(Store):

    instance = None

    def getVersion(self):
        """
        Gets the current version of Maya as a string.

        Returns:
            (string): Version number
        """
        if self._version:
            return self._version

        version = ue.SystemLibrary.get_engine_version().split('.')
        self._version = f'{version[0]}.{version[1]}'  # only include major and minor revision, excluding bug and build
        return self._version


def create():
    """
    Creates the store, only one instance can exist, making it a singleton.

    Returns:
        (MayaStore): Stores variables that can persist through application sessions.
    """
    if UnrealStore.instance is None:
        UnrealStore.instance = UnrealStore(defaults=ucfg.store_defaults)

    return UnrealStore.instance


unreal_store = create()
