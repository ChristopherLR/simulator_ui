from enum import Enum, auto
import threading
import json
import socket
import time
import serial
from dataclasses import dataclass

class ConnectionStatus(Enum):
  CONNECTED = auto()
  DISCONNECTED = auto()

class ProcessingStatus(Enum):
  WAITING_FOR_CONNECTION = auto()
  WAITING_FOR_HEARTBEAT = auto()
  WAITING_FOR_FLOW = auto()

@dataclass
class Configuration():
  simulator_version: str = 'unknown'
  ui_version: str = '0.1.0'
  delay: int = 0
  flow: float = 0.0
  duration: int = 0


class Simulator(threading.Thread):

  def __init__(self):
    threading.Thread.__init__(self, daemon=True)

    self.connection_status = ConnectionStatus.DISCONNECTED
    self.processing_status = ProcessingStatus.WAITING_FOR_CONNECTION
    self.address = None
    self.dev = None
    self.on_success_callback = self.on_success
    self.on_failure_callback = self.on_failure
    self.running = False
    self.configuration = Configuration()
    self.on_update_callback = self.update_callback
    self.simulation_ready_callback = self.simulation_ready
    self.simulation_not_ready_callback = lambda: None
    self.on_flow_callback = self.on_new_data
    self.on_simulation_start_cbs = []
    self.error_count = 0

  def on_new_data(self, ts, flow):
    print(ts, flow)

  def add_simulation_start_callback(self, callback):
    self.on_simulation_start_cbs.append(callback)

  def simulation_ready(self):
    print("Simulation is ready")

  def update_callback(self, configuration):
    print(configuration)

  def check_simulation_ready(self):
    ready = True
    if self.connection_status == ConnectionStatus.DISCONNECTED:
      ready = False
    if self.configuration.flow <= 10:
      ready = False
    if self.configuration.duration <= 1000:
      ready = False
    if ready == True:
      self.simulation_ready_callback()
    if ready == False:
      self.simulation_not_ready_callback()

  def update_configuration(self, flow = None, duration = None, delay = None, simulator_version = None):
    if flow is not None: self.configuration.flow = flow
    if duration is not None: self.configuration.duration = duration 
    if delay is not None: self.configuration.delay = delay 
    if simulator_version is not None: self.configuration.simulator_version = simulator_version 
    self.on_update_callback(self.configuration)
    self.check_simulation_ready()
    
  def update_flow(self, flow: float):
    self.configuration.flow = flow
    self.on_update_callback(self.configuration)

  def update_delay(self, delay: int):
    self.configuration.delay = delay
    self.on_update_callback(self.configuration)

  def update_length(self, length: int):
    self.configuration.length = length
    self.on_update_callback(self.configuration)

  def on_success(self):
    print("Connection Successful")

  def on_failure(self, msgs):
    print(f"Connection Failed: {msgs}")

  def connect(self, address, on_failure, on_success):
    self.error_count = 0
    self.on_success_callback = on_success
    self.on_failure_callback = on_failure
    self.address = address
    self.connection_status = ConnectionStatus.DISCONNECTED
    if self.running == False:
      self.running = True
      self.start()

  def get_hardware_version(self, dev, errors):
    msg = { 'type': 'connect', 'version': self.configuration.ui_version }
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

    self.update_configuration(simulator_version = data['version'])
    return 1

  def start_simulation(self):
    for cb in self.on_simulation_start_cbs:
      cb()

    start_flow = { 
      'type': 'const', 
      'delay': self.configuration.delay, 
      'flow': self.configuration.flow, 
      'length': self.configuration.duration
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
        self.on_failure_callback(errors)
      else:
        err = self.get_hardware_version(dev, errors)
        if err == 0:
          self.on_failure_callback(errors)
          return -1
        self.connection_status = ConnectionStatus.CONNECTED
        self.processing_status = ProcessingStatus.WAITING_FOR_HEARTBEAT
        self.on_success_callback()
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
          self.on_failure_callback([e])
      elif self.processing_status == ProcessingStatus.WAITING_FOR_FLOW:
        line = self.dev.readline()
        msg = line.rstrip().decode('utf-8')
        if msg[0] == 'f':
          [ts, flow] = msg[2:].split(',')
          self.on_flow_callback(int(ts), float(flow))
        elif msg == 'alive':
          self.processing_status = ProcessingStatus.WAITING_FOR_HEARTBEAT

      else:
        time.sleep(0.5)
      




simulator = Simulator()