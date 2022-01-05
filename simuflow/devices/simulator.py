from enum import Enum, auto
import threading
import json
import time
import serial
from simuflow.configuration import * 

class ConnectionStatus(Enum):
  CONNECTED = auto()
  DISCONNECTED = auto()

class ProcessingStatus(Enum):
  WAITING_FOR_CONNECTION = auto()
  WAITING_FOR_HEARTBEAT = auto()
  WAITING_FOR_FLOW = auto()

class Callback(Enum):
  ON_METADATA_UPDATE = auto()
  ON_CONNECTION_SUCCESS = auto()
  ON_CONNECTION_FAILURE = auto()
  ON_FLOW_DATA = auto()
  ON_SIMULATION_READY = auto()
  ON_SIMULATION_START = auto()
  ON_MANUAL_FLOW_UPDATE = auto()
  ON_CONST_FLOW_UPDATE = auto()
  ON_TRIGGER_UPDATE = auto()


class Simulator(threading.Thread):

  def __init__(self):
    threading.Thread.__init__(self, daemon=True)

    self.metadata = SimulatorMetadata()
    self.connection_status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    self.processing_status: ProcessingStatus = ProcessingStatus.WAITING_FOR_CONNECTION
    self.flow_configuration: FlowConfiguration = None
    self.trigger_configuration: TriggerConfiguration = None
    self.address = None
    self.dev = None
    self.running = False
    self.error_count = 0
    self.cb_map = {
      Callback.ON_CONNECTION_SUCCESS: [],
      Callback.ON_CONNECTION_FAILURE: [],
      Callback.ON_CONST_FLOW_UPDATE: [],
      Callback.ON_MANUAL_FLOW_UPDATE: [],
      Callback.ON_SIMULATION_START: [],
      Callback.ON_SIMULATION_READY: [],
      Callback.ON_FLOW_DATA: [],
      Callback.ON_TRIGGER_UPDATE: [],
    }

  def register(self, name: Callback, fn):
    self.cb_map[name].append(fn)

  def check_simulation_ready(self):
    if self.connection_status == ConnectionStatus.DISCONNECTED:
      self.call_cb(Callback.ON_SIMULATION_READY, False)
      return

    if self.flow_configuration == None:
      self.call_cb(Callback.ON_SIMULATION_READY, False)
      return

    if type(self.flow_configuration) == ConstantFlow:
      if self.flow_configuration.duration <= 1000:
        self.call_cb(Callback.ON_SIMULATION_READY, False)
        return

    #if self.configuration.flow_type == FlowType.MANUAL:
      # No logic here yet
    self.call_cb(Callback.ON_SIMULATION_READY, True)

  def call_cb(self, name: Callback, *data):
    for cb in self.cb_map[name]: cb(data)

  def update_configuration(self, config):
    if type(config) == ConstantFlow or type(config) == ManualFlow: 
      self.flow_configuration = config
      self.call_cb(config.cb, self.flow_configuration)

    if type(config) == TriggerConfiguration: 
      self.trigger_configuration = config
      self.call_cb(config.cb, self.trigger_configuration)

    if type(config) == SimulatorMetadata: 
      self.metadata = config
      self.call_cb(config.cb, self.metadata)

    self.check_simulation_ready()
   

  def connect(self, address):
    self.error_count = 0
    self.address = address
    self.connection_status = ConnectionStatus.DISCONNECTED
    if self.running == False:
      self.running = True
      self.start()

  def get_hardware_version(self, dev, errors):
    msg = { 'type': 'connect', 'version': self.metadata.ui_version }
    to_send = bytes(f'{json.dumps(msg)}\r\n', 'utf-8')
    print(f'send: {msg}')
    try:
      dev.write(to_send)
    except Exception as msg:
      self.connection_status = ConnectionStatus.DISCONNECTED
      errors.append(msg)
      return 0

    data = dev.readline()
    data = data.decode('utf-8')
    
    print(data)

    if data == '':
      self.connection_status = ConnectionStatus.DISCONNECTED
      errors.append(TimeoutError(42, "Timeout connecting to device"))
      return 0
    
    try:
      data = json.loads(data)
    except Exception as msg:
      errors.append(TimeoutError(43, "Unable to get hardware version"))
      return 0

    self.metadata.simulator_version = data['version']
    self.update_configuration(self.metadata)
    return 1

  def start_simulation(self):
    self.call_cb(Callback.ON_SIMULATION_START)

    start_flow = { 
      'type': 'const', 
      'delay': self.flow_configuration.delay, 
      'flow': self.flow_configuration.flow, 
      'length': self.flow_configuration.duration
    }
    to_send = bytes(f'{json.dumps(start_flow)}\r\n', 'utf-8')
    print(f'send: {to_send}')
    self.dev.write(to_send)
    self.processing_status = ProcessingStatus.WAITING_FOR_FLOW

  def try_connection(self):
      print(f'Attempting connection: {self.address}')
      errors = []
      dev = None
      try:
        dev = serial.Serial(self.address, 115200, timeout=5)
      except Exception as msg:
        errors.append(msg)

      if dev is None:
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.call_cb(Callback.ON_CONNECTION_FAILURE, *errors)
      else:
        err = self.get_hardware_version(dev, errors)
        if err == 0:
          self.call_cb(Callback.ON_CONNECTION_FAILURE, *errors)
          return -1
        self.connection_status = ConnectionStatus.CONNECTED
        self.processing_status = ProcessingStatus.WAITING_FOR_HEARTBEAT
        self.call_cb(Callback.ON_CONNECTION_SUCCESS)
        self.dev = dev
        self.error_count = 0
        self.check_simulation_ready()

  def run(self):
    while True:
      if self.error_count > 5:
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.processing_status = ProcessingStatus.WAITING_FOR_CONNECTION
      elif self.connection_status == ConnectionStatus.DISCONNECTED:
        err = self.try_connection()
        if err == -1: self.error_count += 1
      elif self.processing_status == ProcessingStatus.WAITING_FOR_HEARTBEAT:
        try:
          data = self.dev.readline()
          data = data.rstrip().decode('utf-8')
          print(data)
        except Exception as e:
          self.error_count += 1
          self.call_cb(Callback.ON_CONNECTION_FAILURE, e)
      elif self.processing_status == ProcessingStatus.WAITING_FOR_FLOW:
        line = self.dev.readline()
        msg = line.rstrip().decode('utf-8')
        if msg[0] == 'f':
          [ts, flow, motor, driver] = msg[2:].split(',')
          print(motor, driver)
          self.call_cb(Callback.ON_FLOW_DATA, int(ts), float(flow), int(motor), int(driver))
        elif msg == 'alive':
          self.processing_status = ProcessingStatus.WAITING_FOR_HEARTBEAT
        else:
          print(msg)

      else:
        time.sleep(0.5)
      




simulator = Simulator()