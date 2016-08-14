from lettuce import world
from PySide.QtGui import QApplication
import sys

if hasattr(world, 'app') == False:
    world.app = QApplication(sys.argv)

