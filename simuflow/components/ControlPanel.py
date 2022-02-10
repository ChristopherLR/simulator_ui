from PySide6.QtWidgets import ( 
  QFrame, QPushButton, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout,
  QWidget, QComboBox, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIntValidator
import os

from simuflow.devices.simulator import simulator, Callback
from simuflow.configuration import *

class ControlPanel(QFrame):
  def __init__(self, parent):
    super(ControlPanel, self).__init__(parent)
    self.setObjectName('ControlPanel')
    self.setStyleSheet("""
    #ControlPanel { 
      margin:0px; 
      border:1px solid black;
      min-width: 300px; 
    }
    """)
    
    label = QLabel(self)
    label.setText('Configuration')
    label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

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
    self.layout.addWidget(camera_delay_input)
    self.layout.addWidget(configuration_view)
    self.layout.addWidget(start)

  def simulation_ready(self, ready):
    val, = ready
    self.start.setEnabled(val)

  def start_simulation(self):
    simulator.start_simulation()

class CameraDelayInput(QFrame):
  def __init__(self, parent):
    super(CameraDelayInput, self).__init__(parent)
    
    set = QPushButton("Set", self)
    set.clicked.connect(self.set_input)

    input = QLineEdit(self)
    input.setPlaceholderText('Camera delay (ms)')
    input.setValidator(QIntValidator())
    self.input = input

    self.layout = QHBoxLayout(self)
    self.layout.addWidget(input)
    self.layout.addWidget(set)
  
  def set_input(self):
    delay = self.input.text()
    input_delay = None

    if delay != '': input_delay = int(delay)

    simulator.update_delay(input_delay)
  

class HarwareSetup(QFrame):
  def __init__(self, parent):
    super(HarwareSetup, self).__init__(parent)
    self.setObjectName('HardwareConfig')
    self.setStyleSheet("""
      #HardwareConfig { 
        margin:0px; 
        padding: 1px;
        border:1px solid black; 
        max-height: 150px;
      }
    """)

    scan = QPushButton("Scan", self)
    scan.clicked.connect(self.list_devices)
    scan.setMaximumWidth(50)

    connect = QPushButton("Connect", self)
    connect.clicked.connect(self.attempt_connection)

    self.input = QComboBox(self)
    self.list_devices()

    self.processing_status = QLabel(simulator.processing_status.name)
    self.processing_status.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

    self.connection_error = QLabel("")
    self.connection_error.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

    connection = QWidget(self)
    connection.layout = QHBoxLayout(connection)
    connection.layout.addWidget(scan)
    connection.layout.addWidget(self.input)
    connection.layout.setContentsMargins(0,0,0,0)
    connection.layout.setSpacing(0)

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(connection)
    self.layout.addWidget(connect)
    self.layout.addWidget(self.processing_status)
    self.layout.addWidget(self.connection_error)

    simulator.register(Callback.ON_CONNECTION_FAILURE, self.on_connection_failure)
    simulator.register(Callback.ON_CONNECTION_SUCCESS, self.on_connection_success)
    # self.layout.setContentsMargins(0,0,0,0)
    # self.layout.setSpacing(0)

  def attempt_connection(self):
    simulator.connect(self.input.currentText())

  def on_connection_success(self, data):
    self.processing_status.setText("Connected")
    self.connection_error.setText("")

  def list_devices(self):
    self.input.clear()
    if os.name == 'nt':  # sys.platform == 'win32':
      from serial.tools.list_ports_windows import comports
    elif os.name == 'posix':
        from serial.tools.list_ports_posix import comports
    else:
        raise ImportError("Sorry: no implementation for your platform ('{}') available".format(os.name))
    iterator = comports()
    for n, (port, desc, hwid) in enumerate(iterator, 1):
      self.input.addItem(port)
      # print(f'n: {n}, port: {port}, desc: {desc}, hwid: {hwid}')

  def on_connection_failure(self, errors):
    print(errors)
    self.processing_status.setText(f"Failed to connect")
    err_string = ""
    for error in errors:
      err_string += f"{error.args}\n"
    self.connection_error.setText(err_string)

class ConfigurationView(QFrame):
  def __init__(self, parent):
    super(ConfigurationView, self).__init__(parent)
    self.setObjectName('ConfigView')
    self.setStyleSheet("""
      #ConfigView { 
        margin:0px; 
        padding: 1px;
        border:1px solid black; 
        max-height: 150px;
      }
    """)

    metadata = simulator.metadata

    simulator.register(Callback.ON_METADATA_UPDATE, self.update_config)

    int_version = QLabel(f'Interface Version: {metadata.ui_version}')
    sim_version = QLabel(f'Simulator Version: {metadata.simulator_version}')

    # delay = QLabel(f"Delay: {config.delay}")
    # flow = QLabel(f"Flow: {config.flow}")
    # duration = QLabel(f"Duration: {config.duration}")

    self.int_version = int_version
    self.sim_version = sim_version
    # self.delay = delay
    # self.flow = flow
    # self.duration = duration

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(int_version)
    self.layout.addWidget(sim_version)
    # self.layout.addWidget(delay)
    # self.layout.addWidget(flow)
    # self.layout.addWidget(duration)

  def update_config(self, config: SimulatorMetadata):
    config, = config
    print(config)
    self.int_version.setText(f'Interface Version: {config.ui_version}')
    self.sim_version.setText(f'Simulator Version: {config.simulator_version}')
    # self.delay.setText(f"Delay: {config.delay}")
    # self.flow.setText(f"Flow: {config.flow}")
    # self.duration.setText(f"Duration: {config.duration}")
