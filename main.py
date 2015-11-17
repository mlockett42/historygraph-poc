# This is the main file for the UI for livewire communicator

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from formmain import *

InitSession()
# Create the Qt Application
app = QApplication(sys.argv)
# Create and show the form
form = FormMain()
form.show()

# Run the main Qt loop
sys.exit(app.exec_())
