import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import QSize
import matplotlib
import asyncio
import signal
import functools

from bs_ui.components.ControlPanel import ControlPanel
from bs_ui.components.ImportPanel import ImportPanel
from bs_ui.components.DisplayPanel import DisplayPanel
from bs_ui.devices.simulator import Simulator

# matplotlib.use('Qt6Agg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle('SimuFlow')
    self.resize(QSize(800, 600))



    layout = QHBoxLayout()
    layout.addWidget(ImportPanel(self))
    layout.addWidget(ControlPanel(self))
    layout.addWidget(DisplayPanel(self))
    layout.setContentsMargins(0,0,0,0)
    layout.setSpacing(0)

    widget = QWidget()
    widget.setLayout(layout)

    self.setCentralWidget(widget)

def stopper(signame, loop):
    print(f'Received {signame}, stopping...')
    loop.stop()

def start():
  loop = asyncio.get_event_loop()
  for signame in ('SIGINT', 'SIGTERM'):
    loop.add_signal_handler(getattr(signal, signame), functools.partial(stopper, signame, loop))

  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  app.exec()

if __name__ == '__main__':
  start()