import sys
from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QApplication
from PySide6.QtCore import QSize
from simuflow.components.ConfigPanel import ConfigPanel 
from simuflow.components.DisplayPanel import DisplayPanel

class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle('SimuFlow')
    self.resize(QSize(800, 600))


    layout = QHBoxLayout()
    layout.addWidget(ConfigPanel(self))
    layout.addWidget(DisplayPanel(self))
    layout.setContentsMargins(0,0,0,0)
    layout.setSpacing(0)

    widget = QWidget()
    widget.setLayout(layout)

    self.setCentralWidget(widget)

def start():
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  app.exec()

if __name__ == '__main__':
  start()