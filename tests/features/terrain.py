from lettuce import world
from PySide.QtGui import QApplication
import sys
import os

if hasattr(world, 'app') == False:
    world.app = QApplication(sys.argv)
    world.demux = None
    world.formsettings = None
    if os.path.exists('/tmp/testdump.db'):
        os.remove('/tmp/testdump.db')
    else:
        pass
    if os.path.exists('/tmp/output.txt'):
        os.remove('/tmp/output.txt')
    else:
        pass


