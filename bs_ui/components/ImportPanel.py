from PySide6.QtWidgets import ( 
  QFrame, QWidget, QVBoxLayout, QPushButton, QTabWidget, QLabel,
  QLineEdit, QHBoxLayout, QPushButton
)
from PySide6.QtCore import QBuffer, Qt, QSize
from PySide6.QtGui import QIntValidator, QDoubleValidator
from bs_ui.components.Graph import Graph, Canvas
from bs_ui.devices.simulator import simulator

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

    flow_box = QWidget(self)
    flow_label = QLabel("Flow (L/min)")
    flow_input = QLineEdit(flow_box)
    flow_input.setValidator(QDoubleValidator())
    flow_box.layout = QHBoxLayout(flow_box)
    flow_box.layout.addWidget(flow_label)
    flow_box.layout.addWidget(flow_input)

    self.flow_input = flow_input

    duration_box = QWidget(self)
    duration_label = QLabel("Duration (ms)")
    duration_input = QLineEdit(duration_box)
    duration_input.setValidator(QIntValidator())
    duration_box.layout = QHBoxLayout(duration_box)
    duration_box.layout.addWidget(duration_label)
    duration_box.layout.addWidget(duration_input)

    self.duration_input = duration_input

    set_button = QPushButton("Set")
    set_button.clicked.connect(self.set_input)

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(flow_box)
    self.layout.addWidget(duration_box)
    self.layout.addWidget(set_button)

  def set_input(self):
    flow = self.flow_input.text()
    duration = self.duration_input.text()
    input_flow = None
    input_duration = None

    if flow != '': input_flow = float(flow)
    if duration != '': input_duration = int(duration)

    simulator.update_configuration(flow=input_flow, duration=input_duration)

class DynamicFlowPanel(QFrame):
  def __init__(self, parent):
    super(DynamicFlowPanel, self).__init__(parent)

    button = QPushButton("Import")

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(button)