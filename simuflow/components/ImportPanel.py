from PySide6.QtWidgets import ( 
  QFrame, QWidget, QVBoxLayout, QPushButton, QTabWidget, QLabel,
  QLineEdit, QHBoxLayout, QPushButton, QRadioButton
)
from PySide6.QtCore import QBuffer, Qt, QSize
from PySide6.QtGui import QIntValidator, QDoubleValidator
from simuflow.components.Graph import Graph, Canvas
from simuflow.devices.simulator import simulator

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
    tabs.addTab(ManualFlowPanel(self), "Manual Flow")
    tabs.addTab(DynamicFlowPanel(self), "Dynamic Flow")

    graph = Canvas(self, 10000, 200)
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

class ManualFlowPanel(QFrame):
  def __init__(self, parent):
    super(ManualFlowPanel, self).__init__(parent)

    motor_box = QWidget(self)
    motor_label = QLabel("Fan")
    motor_on = QRadioButton("On")
    motor_on.setChecked(True)
    motor_off = QRadioButton("Off")
    motor_off.setChecked(False)
    motor_box.layout = QHBoxLayout(motor_box)
    motor_box.layout.addWidget(motor_label)
    motor_box.layout.addWidget(motor_on)
    motor_box.layout.addWidget(motor_off)

    self.motor_on = motor_on 
    self.motor_off = motor_off

    # Fan control
    fc = QWidget(self)
    fc_label = QLabel("Fan Control")
    fc_input = QLineEdit(fc)
    fc_input.setValidator(QIntValidator())
    fc.layout = QHBoxLayout(fc)
    fc.layout.addWidget(fc_label)
    fc.layout.addWidget(fc_input)

    self.fc_input = fc_input 

    # Driver control
    dc = QWidget(self)
    dc_label = QLabel("Driver Control")
    dc_input = QLineEdit(dc)
    dc_input.setValidator(QIntValidator())
    dc.layout = QHBoxLayout(dc)
    dc.layout.addWidget(dc_label)
    dc.layout.addWidget(dc_input)

    self.dc_input = fc_input 

    set_button = QPushButton("Set")
    set_button.clicked.connect(self.set_input)

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(motor_box)
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