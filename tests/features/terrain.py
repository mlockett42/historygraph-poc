from lettuce import world
from PySide.QtGui import QApplication
import sys
import os

def removepath(pathname):
    if os.path.exists(pathname):
        os.remove(pathname)
    else:
        pass

if hasattr(world, 'app') == False:
    world.app = QApplication(sys.argv)
    world.demux1 = None
    world.demux2 = None
    world.formsettings = None
    removepath('/tmp/testdump1.db')
    removepath('/tmp/testdump2.db')
    removepath('/tmp/output.txt')


