from PySide6.QtWidgets import ( 
  QFrame, QPushButton, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout,
  QWidget
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIntValidator

from bs_ui.devices.simulator import simulator

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
    # start.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)


    camera_delay_input = CameraDelayInput(self)

    hardware_setup = HarwareSetupPanel(self)

    self.layout = QVBoxLayout(self)
    self.layout.addWidget(label)
    self.layout.addWidget(hardware_setup)
    self.layout.addWidget(camera_delay_input)
    self.layout.addWidget(start)

class CameraDelayInput(QFrame):
    def __init__(self, parent):
      super(CameraDelayInput, self).__init__(parent)
      
      set = QPushButton("Set", self)

      input = QLineEdit(self)
      input.setPlaceholderText('Camera delay (ms)')
      input.setValidator(QIntValidator())

      self.layout = QHBoxLayout(self)
      self.layout.addWidget(input)
      self.layout.addWidget(set)

class HarwareSetupPanel(QFrame):
  def __init__(self, parent):
    super(HarwareSetupPanel, self).__init__(parent)
    self.setObjectName('HardwareConfig')
    self.setStyleSheet("""
      #HardwareConfig { 
        margin:0px; 
        padding: 1px;
        border:1px solid black; 
        max-height: 80px;
      }
    """)

    connect = QPushButton("Connect", self)
    connect.clicked.connect(self.attempt_connection)

    self.input = QLineEdit(self)
    self.input.setPlaceholderText("IP Address: 192.168.1.12")

    self.connection_status = QLabel(simulator.connection_status.name)
    self.connection_status.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

    self.connection_error = QLabel("")
    self.connection_error.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

    connection = QWidget(self)
    connection.layout = QHBoxLayout(connection)
    connection.layout.addWidget(self.input)
    connection.layout.addWidget(connect)
    connection.layout.setContentsMargins(0,0,0,0)
    connection.layout.setSpacing(0)



    self.layout = QVBoxLayout(self)
    self.layout.addWidget(connection)
    self.layout.addWidget(self.connection_status)
    self.layout.addWidget(self.connection_error)
    self.layout.setContentsMargins(0,0,0,0)
    self.layout.setSpacing(0)

  def attempt_connection(self):
    simulator.connect(self.input.text(), self.on_connection_failure, self.on_connection_success)

  def on_connection_success(self):
    self.connection_status.setText("Connected")
    self.connection_error.setText("")

  def on_connection_failure(self, errors):
    print(errors)
    self.connection_status.setText(f"Failed to connect")
    err_string = ""
    for error in errors:
      number, message = error.args
      if number == 8:
        err_string += f"Incorrect format for address\n"
      else:
        err_string += f"{message}: {number}\n"
    self.connection_error.setText(err_string)