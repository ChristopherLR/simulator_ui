from enum import Enum, auto
import threading
import json
import time
import serial
from simuflow.configuration import * 
from simuflow.packet import ConfigurationPacket

class ConnectionStatus(Enum):
  CONNECTED = auto()
  DISCONNECTED = auto()

class ThreadState(Enum):
  UNINITIALIZED = auto()
  RUNNING = auto()
  SLEEPING = auto()

class ProcessingStatus(Enum):
  WAITING_FOR_CONNECTION = auto()
  ATTEMPTING_CONNECTION = auto()
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
    self.processing_status: ProcessingStatus = ProcessingStatus.WAITING_FOR_CONNECTION
    self.flow_configuration: FlowConfiguration = None
    self.trigger_configuration: TriggerConfiguration = TriggerConfiguration() 
    self.address = None
    self.dev = None
    self.thread_state = ThreadState.UNINITIALIZED 
    self.error_count = 0
    self.hb_count = 0
    self.cb_map = {
      Callback.ON_METADATA_UPDATE: [],
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
    print(f'Register: {name}')
    self.cb_map[name].append(fn)

  def check_simulation_ready(self):
    if self.processing_status == ProcessingStatus.WAITING_FOR_CONNECTION:
      self.call_cb(Callback.ON_SIMULATION_READY, False)
      return

    if self.processing_status == ProcessingStatus.ATTEMPTING_CONNECTION:
      self.call_cb(Callback.ON_SIMULATION_READY, False)
      return

    if self.flow_configuration == None:
      self.call_cb(Callback.ON_SIMULATION_READY, False)
      return

    if type(self.flow_configuration) == ConstantFlow:
      if self.flow_configuration.validate() == False:
        self.call_cb(Callback.ON_SIMULATION_READY, False)
        return

    #if self.configuration.flow_type == FlowType.MANUAL:
      # No logic here yet
    self.call_cb(Callback.ON_SIMULATION_READY, True)

  def call_cb(self, name: Callback, *data: None):
    for cb in self.cb_map[name]: cb(data)

  def update_configuration(self, config):
    print(f'Update configuration: {config}')
    if type(config) == ConstantFlow:
      self.flow_configuration = config
      self.call_cb(Callback.ON_CONST_FLOW_UPDATE, self.flow_configuration)

    if type(config) == ManualFlow: 
      self.flow_configuration = config
      self.call_cb(Callback.ON_MANUAL_FLOW_UPDATE, self.flow_configuration)

    if type(config) == TriggerConfiguration: 
      self.trigger_configuration = config
      self.call_cb(Callback.ON_TRIGGER_UPDATE, self.trigger_configuration)

    if type(config) == SimulatorMetadata: 
      self.metadata = config
      self.call_cb(Callback.ON_METADATA_UPDATE, self.metadata)

    self.check_simulation_ready()
   

  def connect(self, address):
    print(address)
    self.error_count = 0
    self.address = address
    self.processing_status = ProcessingStatus.ATTEMPTING_CONNECTION
    if self.thread_state == ThreadState.UNINITIALIZED:
      self.thread_state = ThreadState.RUNNING
      self.start()
    
    if self.thread_state == ThreadState.SLEEPING:
      self.thread_state = ThreadState.RUNNING

  def get_hardware_version(self, dev, errors):
    msg = { 't': 'connect', 'version': self.metadata.ui_version }
    to_send = bytes(f'{json.dumps(msg)}\r\n', 'utf-8')
    print(f'send: {msg}')
    try:
      dev.write(to_send)
    except Exception as msg:
      self.processing_status = ProcessingStatus.WAITING_FOR_CONNECTION
      errors.append(msg)
      return 0

    data = dev.readline()
    data = data.decode('utf-8')
    
    print(data)

    if data == '':
      self.processing_status = ProcessingStatus.WAITING_FOR_CONNECTION
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
    packet = ConfigurationPacket()

    if type(self.flow_configuration) == ConstantFlow:
      packet.flow_type = ConstantFlow
      packet.delay = self.trigger_configuration.delay
      packet.flow = self.flow_configuration.flow
      packet.duration = self.flow_configuration.duration
    
    if type(self.flow_configuration) == ManualFlow:
      packet.flow_type = ManualFlow
      packet.motor_state = self.flow_configuration.motor_state
      packet.driver = self.flow_configuration.driver
      packet.motor = self.flow_configuration.fan

    to_send = packet.toBytes()
    print(f'send: {to_send}')

    error = False
    try:
      self.dev.write(to_send)
    except Exception as e:
      print(f'Error writing to device: {e}')
      error = True

    del packet

    if error == False:
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
        self.processing_status = ProcessingStatus.WAITING_FOR_CONNECTION
        self.call_cb(Callback.ON_CONNECTION_FAILURE, *errors)
      else:
        err = self.get_hardware_version(dev, errors)
        if err == 0:
          self.call_cb(Callback.ON_CONNECTION_FAILURE, *errors)
          return -1
        self.processing_status = ProcessingStatus.WAITING_FOR_HEARTBEAT
        self.call_cb(Callback.ON_CONNECTION_SUCCESS, True)
        self.dev = dev
        self.error_count = 0
        self.check_simulation_ready()
  
  def process_message(self, msg):
    data = msg.rstrip().decode('utf-8')
    # print(f'recv: {data}')
    if data == 'alive':
      print(f'heartbeat received: {self.hb_count}\r', end = '')
      self.hb_count += 1
    else:
      print(data)
      try:
        data = json.loads(data)
      except Exception as e:
        print(e)
      if 'version' in data:
        self.metadata.simulator_version = data['version']
        self.call_cb(Callback.ON_METADATA_UPDATE, self.metadata)

  def run(self):
    print('Sim thread running')
    while True:
      if self.error_count > 5:
        self.processing_status = ProcessingStatus.WAITING_FOR_CONNECTION
        self.error_count = 0
      elif self.processing_status == ProcessingStatus.ATTEMPTING_CONNECTION:
        err = self.try_connection()
        if err == -1: self.error_count += 1
      elif self.processing_status == ProcessingStatus.WAITING_FOR_HEARTBEAT:
        try:
          data = self.dev.readline()
          self.process_message(data)
        except Exception as e:
          self.error_count += 1
          self.call_cb(Callback.ON_CONNECTION_FAILURE, e)
      elif self.processing_status == ProcessingStatus.WAITING_FOR_FLOW:
        line = self.dev.readline()
        msg = line.rstrip().decode('utf-8')
        if len(msg) == 0: continue
        if msg[0] == 'f':
          # [ts, flow, motor, driver] = msg[2:].split(',')
          [ts, flow] = msg[2:].split(',')
          # print(motor, driver)
          self.call_cb(Callback.ON_FLOW_DATA, int(ts), float(flow))
        elif msg == 'alive':
          self.processing_status = ProcessingStatus.WAITING_FOR_HEARTBEAT
        else:
          print(f'recv: {msg}')

      else:
        self.thread_state = ThreadState.SLEEPING 
        time.sleep(0.1)
      




simulator = Simulator()