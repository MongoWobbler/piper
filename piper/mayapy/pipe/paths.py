#  Copyright (c) Christian Corsica. All Rights Reserved.

import pymel.core as pm

import piper.config.maya as mcfg
from piper.core.dcc.template.paths import PathDCC
from piper.mayapy.pipe.store import maya_store


class MayaPaths(PathDCC):

    def display(self, text):
        """
        Way of DCC of displaying text in a friendly, visible manner.

        Args:
            text (string): Text to display.
        """
        pm.displayInfo(text)

    def warn(self, text):
        """
        Way of DCC to warn user of with message.

        Args:
            text (string): Text to warn user with.
        """
        pm.warning(text)

    def getCurrentScene(self):
        """
        Meant to be overridden by DCC that can get the full path to the currently opened scene in the DCC.

        Returns:
            (string): Full path to the current scene.
        """
        return pm.sceneName()

    def getCurrentProject(self):
        """
        Uses the DCC store to get the current project selected.

        Returns:
            (string): Name of current project selected.
        """
        return maya_store.get(mcfg.current_project)

    def setCurrentProject(self, project=None, force=False):
        """
        Sets the given project on the Maya store.

        Args:
            project (string): If given, will set the current project to the given project.

            force (boolean): If True, will force to set the project to None if None is given.

        Returns:
            (boolean): True if project was set, False if it was not set.
        """
        if project or force:
            maya_store.set(mcfg.current_project, project)
            return True

        return False


maya_paths = MayaPaths()
