from PySide6.QtWidgets import ( 
  QFrame, QWidget, QVBoxLayout, QPushButton, QTabWidget, QLabel,
  QLineEdit, QHBoxLayout, QPushButton, QRadioButton, QFileDialog,
)
from PySide6.QtCore import QBuffer, Qt, QSize
from PySide6.QtGui import QIntValidator, QDoubleValidator
from simuflow.components.Graph import Graph, Canvas
from simuflow.components.ControlPanel import CameraDelayInput, HarwareSetup, ConfigurationView 
from simuflow.devices.simulator import simulator, Callback
from simuflow.configuration import *
import csv
import re
from scipy import interpolate
import numpy as np

class ConfigPanel(QFrame):
  def __init__(self, parent):
    super(ConfigPanel, self).__init__(parent)
    self.setObjectName('ConfigPanel')
    self.setStyleSheet("""
      #ConfigPanel { 
        margin:0px; 
        border:1px solid black; 
        min-width: 150px;
        max-width: 350px;
      }
    """)

    label = QLabel(self)
    label.setText('Configuration')
    label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

    flow_configuration = FlowConfiguration(self)

    start = QPushButton("Start")
    start.setEnabled(False)
    start.clicked.connect(self.start_simulation)

    simulator.register(Callback.ON_SIMULATION_READY, self.simulation_ready)
    self.start = start
    # start.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)


    camera_delay_input = CameraDelayInput(self)

    hardware_setup = HarwareSetup(self)

    configuration_view = ConfigurationView(self)

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(label)
    self.layout.addWidget(hardware_setup)
    self.layout.addWidget(flow_configuration)
    self.layout.addWidget(camera_delay_input)
    self.layout.addWidget(configuration_view)
    self.layout.addWidget(start)
    

  
  def simulation_ready(self, ready):
    val, = ready
    self.start.setEnabled(val)

  def start_simulation(self):
    simulator.start_simulation()

class FlowConfiguration(QFrame):
  def __init__(self, parent):
    super(FlowConfiguration, self).__init__(parent)
    self.setObjectName('FlowConfig')
    self.setStyleSheet("""
      #FlowConfig { 
        margin:0px; 
        min-width: 150px;
        max-width: 350px;
      }
    """)

    tabs = QTabWidget()
    tabs.setTabPosition(QTabWidget.North)
    tabs.setMovable(False)
    tabs.addTab(ConstantFlowPanel(self), "Constant Flow")
    # tabs.addTab(ManualFlowPanel(self), "Manual Flow")
    tabs.addTab(DynamicFlowPanel(self), "Dynamic Flow")

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(tabs)

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
    config = ConstantFlow()
    flow = self.flow_input.text()
    duration = self.duration_input.text()

    if flow != '': config.flow = float(flow)
    if duration != '': config.duration = int(duration)

    simulator.update_configuration(config)

class ManualFlowPanel(QFrame):
  def __init__(self, parent):
    super(ManualFlowPanel, self).__init__(parent)

    # Motor Toggle
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

    self.dc_input = dc_input 

    set_button = QPushButton("Set")
    set_button.clicked.connect(self.set_input)

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(motor_box)
    self.layout.addWidget(fc)
    self.layout.addWidget(dc)
    self.layout.addWidget(set_button)


  def set_input(self):
    config = ManualFlow()
    print(f'motor on: {self.motor_on.isChecked()}')
    print(f'motor off: {self.motor_off.isChecked()}')
    if self.motor_on.isChecked(): config.motor_state = 1
    if self.motor_off.isChecked(): config.motor_state = 0
    driver = self.dc_input.text()
    if driver != '': config.driver = int(driver)
    fan = self.fc_input.text()
    if fan != '': config.fan = int(fan)

    simulator.update_configuration(config)



class DynamicFlowPanel(QFrame):
  def __init__(self, parent):
    super(DynamicFlowPanel, self).__init__(parent)

    self.button = QPushButton("Import")
    self.button.clicked.connect(self.import_csv)
    self.confirm= QPushButton("Confirm")
    self.confirm.clicked.connect(self.confirm_data)

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(self.button)
    self.layout.addWidget(self.confirm)

  def confirm_data(self):
    simulator.confirm_dynamic_profile()

  def import_csv(self):
      (fname, _) = QFileDialog.getOpenFileName(self, "Open Data File", "", "CSV data files (*.csv)")
      print(fname)
      xdata = []
      ydata = []

      time_multiplicand = {
        's': 1000.0,
        'second': 1000.0,
        'seconds': 1000.0,
        'ms': 1.0,
        'millisecond': 1.0,
        'milliseconds': 1.0,
      }

      flow_multiplicand = {
        'L/m': 1.0,
        'L/min': 1.0,
        'L/s': 1/60,
        'L/second': 1/60,
      }

      with open(fname) as input_file:
        reader = csv.reader(input_file)
        time_mul = None
        flow_mul = None
        
        for idx, row in enumerate(reader):
          if idx == 0:
            time, flow = row
            m_time = re.search(r'time\((.*)\)', time)
            m_flow = re.search(r'flow\((.*)\)', flow)
            if m_time == None or m_flow == None:
              print('Time or flow now specified assuming ms and L/m')
              time_mul = time_multiplicand['ms']
              flow_mul = time_multiplicand['L/m']
            else:
              print(f'Using {time} and {flow}')
              time_mul = time_multiplicand[m_time[1]]
              flow_mul = flow_multiplicand[m_flow[1]]

            if time_mul == None or flow_mul == None:
              print(f'Error getting multiplicands, time: {time}, flow: {flow}')
              return
          else:
            time, flow = row
            xdata.append(int(float(time)*time_mul))
            ydata.append(float(flow)*flow_mul)

      f = interpolate.interp1d(xdata, ydata)
      interp_x = np.arange(min(xdata), max(xdata), 20)
      interp_y = f(interp_x)
      print(f'Parsed data {len(interp_x)}, {len(interp_y)}')
      flow_config = DynamicFlow(list(interp_x), list(interp_y))

      simulator.update_configuration(flow_config)