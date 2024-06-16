#  Copyright (c) Christian Corsica. All Rights Reserved.

import pymel.core as pm

from piper.core.perforce import Perforce
from piper.ui.widget import getUserInput
from piper.mayapy.ui.widget import getMainWindow
import piper.mayapy.ui.window as window


class PerforceMaya(Perforce):

    def getParentWindow(self):
        """
        Gets the parent window in Maya.

        Returns:
            (QtWidget): Widget to parent to.
        """
        return getMainWindow()

    def getCurrentScene(self):
        """
        Gets the current scene to use in perforce when path is not passed in.

        Returns:
            (string): Full path to scene.
        """
        scene = pm.sceneName()

        if not scene and not window.save():
            pm.error('Please save the scene!')

        return scene

    def askForPassword(self):
        """
        Prompts user for password to input into P4.

        Returns:
            (string): P4 password.
        """
        return getUserInput('Type in your P4 password', 'Password: ', self.getParentWindow(), True)

    def display(self, text):
        """
        Prints out important messages to display bar.

        Args:
            text (string): Text to display.
        """
        pm.displayInfo('P4: ' + text)


def makeAvailable(write_method=None, path=None, add=True, *args, **kwargs):
    """
    Convenience method for making a file available.

    Args:
        write_method (method): Function that writes the file. Args and Kwargs will be passed ot this method.

        path (string or iterable): Path to make available.

        add (boolean): If True, will attempt to add file if not in client.

    Returns:
        (dictionary): Results of all the actions done for each file.
    """
    p4 = PerforceMaya()
    with p4.connect():
        results = p4.makeAvailable(write_method=write_method, path=path, add=add, *args, **kwargs)

    return results


def _save():
    """
    Save method with force flag turned on to save current scene.
    """
    pm.saveFile(f=True)


def save(*args, **kwargs):
    """
    Saves the scene. Checks it out before saving or adds it to P4.
    """
    makeAvailable(_save, *args, **kwargs)
