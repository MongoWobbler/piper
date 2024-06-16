#  Copyright (c) Christian Corsica. All Rights Reserved.


class ExportDCC(object):

    def exportToGame(self):
        """
        Exports the file(s) of the DCC scene to the game directory.
        """
        raise NotImplementedError

    def exportToCurrentDirectory(self):
        """
        Exports the file(s) of the DCC scene to the art directory.
        """
        raise NotImplementedError

    def exportMeshesToCurrentAsObj(self):
        """
        Export the file(s) of the DCC to the art directory as obj format.
        """
        raise NotImplementedError


dcc_export = ExportDCC()
