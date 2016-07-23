from lettuce import world
from PySide.QtGui import QApplication
import sys
from formmain import *

InitSession()

if hasattr(world, 'app') == False:
    world.app = QApplication(sys.argv)

