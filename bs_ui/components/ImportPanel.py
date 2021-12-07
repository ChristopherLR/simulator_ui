from PySide6.QtWidgets import ( 
  QFrame, QWidget, QVBoxLayout, QPushButton, QTabWidget, QLabel
)
from PySide6.QtCore import Qt, QSize
from bs_ui.components.Graph import Graph, Canvas

class ImportPanel(QFrame):
  def __init__(self, parent):
    super(ImportPanel, self).__init__(parent)
    self.setObjectName('ImportPanel')
    self.setStyleSheet("""
      #ImportPanel { 
        margin:0px; 
        border:1px solid black; 
        min-width: 350px;
      }
    """)

    label = QLabel(self)
    label.setText('Input')
    label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
    
    tabs = QTabWidget()
    tabs.setTabPosition(QTabWidget.North)
    tabs.setMovable(False)
    tabs.addTab(ConstantFlowPanel(self), "Constant Flow")
    tabs.addTab(DynamicFlowPanel(self), "Dynamic Flow")

    graph = Canvas(self)
    graph.setMaximumHeight(250)

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(label)
    self.layout.addWidget(tabs)
    self.layout.addWidget(graph, Qt.AlignHCenter)

class ConstantFlowPanel(QFrame):
  def __init__(self, parent):
    super(ConstantFlowPanel, self).__init__(parent)

    button = QPushButton("Import")

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(button)

class DynamicFlowPanel(QFrame):
  def __init__(self, parent):
    super(DynamicFlowPanel, self).__init__(parent)

    button = QPushButton("Import")

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(button)