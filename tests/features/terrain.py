from lettuce import world
from PySide.QtGui import QApplication
import sys
import os
import utils

def removepath(pathname):
    utils.log_output("removepath(",pathname,")")
    if os.path.exists(pathname):
        os.remove(pathname)
    else:
        pass



if hasattr(world, 'app') == False:
    world.app = QApplication(sys.argv)
    world.demux1 = None
    world.demux2 = None
    world.formsettings = None
    world.formmain = None
    utils.removepath('/tmp/output.txt')
    utils.removepath('/tmp/testdump1.db')
    utils.removepath('/tmp/testdump2.db')


