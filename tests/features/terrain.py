from lettuce import world
from PySide.QtGui import QApplication
import sys
import os

if hasattr(world, 'app') == False:
    world.app = QApplication(sys.argv)
    if os.path.exists('/tmp/testdump.db'):
        os.remove('/tmp/testdump.db')
    else:
        pass

