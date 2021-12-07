from PySide6.QtWidgets import QVBoxLayout, QFrame, QWidget, QPushButton, QLabel
from PySide6.QtCore import QSize, Qt

from bs_ui.components.Graph import Canvas 

class DisplayPanel(QFrame):
  def __init__(self, parent):
    super(DisplayPanel, self).__init__(parent)
    self.setObjectName('DisplayPanel')
    self.setStyleSheet("""
      #DisplayPanel { 
        margin:0px; 
        border:1px solid black; 
        min-width: 350px;
      }
    """)

    label = QLabel(self)
    label.setText('Output')
    label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
    
    self.layout = QVBoxLayout(self)

    graph = Canvas(self)
    graph.setFixedHeight(250)
    # graph.fig.axes.plot([0,1,2,3,4], [10,1,20,3,40])

    self.layout.addWidget(label)
    self.layout.addWidget(graph)

    self.button = QPushButton("Export")
    self.layout.addWidget(self.button)