#  Copyright (c) Christian Corsica. All Rights Reserved.

import sys
from PySide2.QtWidgets import QApplication
import piper.core.util as pcu
import piper.core.vendor as vendor


pcu.setPiperDirectory()
vendor.addPaths(error=False)

if __name__ == '__main__':
    import piper.ui.installer
    app = QApplication(sys.argv)
    window = piper.ui.installer.MainWindow()
    window.show()
    sys.exit(app.exec_())
