#  Copyright (c) Christian Corsica. All Rights Reserved.

from piper.core.dcc.template.paths import dcc_paths


class WidgetDCC(object):

    def __init__(self):
        """
        Used as template of common widget functionality across different DCCs.
        """
        self.dcc_paths = dcc_paths

    def setArtDirectory(self, *args, **kwargs):
        """
        Opens up a dialog window for the user to select the art directory they would like the current project to have.

        Returns:
            (string): Path to directory user has selected.
        """
        return NotImplementedError

    def setGameDirectory(self, *args, **kwargs):
        """
        Opens up a dialog window for the user to select the game directory they would like the current project to have.

        Returns:
            (string): Path to directory user has selected.
        """
        return NotImplementedError
