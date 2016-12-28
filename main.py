# This is the main file for the UI for livewire communicator

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from formmain import *
from Demux import Demux

# Create the Qt Application
app = QApplication(sys.argv)
# Create and show the form
form = FormMain(parent = None, demux=Demux(fromfile = 'historygraph.db'))
form.show()

# Run the main Qt loop
sys.exit(app.exec_())
