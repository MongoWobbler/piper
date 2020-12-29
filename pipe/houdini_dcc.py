#  Copyright (c) 2021 Christian Corsica. All Rights Reserved.

from pipe.dcc import DCC


class Houdini(DCC):

    def __init__(self):
        super(Houdini, self).__init__()
        self.registry_path = 'SOFTWARE\\Side Effects Software'
        self.registry_exclude = 'Houdini'
        self.registry_install_key = 'InstallPath'
        self.registry_install_path = 'SOFTWARE\\Side Effects Software\\{}'.format(self.version_replace)
        self.relative_python_path = ['bin', 'hython.exe']
        self.relative_batch_path = ['bin', 'houdini.exe']
