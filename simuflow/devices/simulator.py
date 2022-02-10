from enum import Enum, auto
import threading
import json
import time
from typing import Any, Optional
import serial
from simuflow.configuration import * 
from simuflow.packet import ConfigurationPacket
from copy import copy
from math import isclose

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
  WAITING_FOR_PROFILE_CONFIRMATION = auto()
  SENDING_DYNAMIC_PROFILE = auto()

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
  ON_DYNAMIC_FLOW_UPDATE = auto()


class Simulator(threading.Thread):

  def __init__(self):
    threading.Thread.__init__(self, daemon=True)

    self.metadata = SimulatorMetadata()
    self.processing_status: ProcessingStatus = ProcessingStatus.WAITING_FOR_CONNECTION
    self.flow_configuration: Optional[FlowConfiguration] = None 
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
      Callback.ON_DYNAMIC_FLOW_UPDATE: [self.send_dynamic_profile],
      Callback.ON_SIMULATION_START: [],
      Callback.ON_SIMULATION_READY: [],
      Callback.ON_FLOW_DATA: [],
      Callback.ON_TRIGGER_UPDATE: [],
    }
    self.acknowledged = {}

  def cleanup(self):
    if self.dev != None and self.dev.is_open:
      self.dev.close()

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

  def call_cb(self, name: Callback, *data: Optional[Any]):
    for cb in self.cb_map[name]: cb(data)

  def update_configuration(self, config):
    print(f'Update configuration: {config}')
    if type(config) == ConstantFlow:
      self.flow_configuration = config
      self.call_cb(Callback.ON_CONST_FLOW_UPDATE, self.flow_configuration)

    if type(config) == ManualFlow: 
      self.flow_configuration = config
      self.call_cb(Callback.ON_MANUAL_FLOW_UPDATE, self.flow_configuration)

    if type(config) == DynamicFlow: 
      self.flow_configuration = config
      self.call_cb(Callback.ON_DYNAMIC_FLOW_UPDATE, self.flow_configuration)

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
    assert(self.dev)
    assert(self.flow_configuration)

    self.call_cb(Callback.ON_SIMULATION_START)
    packet = ConfigurationPacket()

    if isinstance(self.flow_configuration, DynamicFlow):
      for idx, k in enumerate(self.acknowledged):
        if self.acknowledged[k]['ack'] == False:
          print(k, self.acknowledged[k])
      msg = { 't': 'run' }
      to_send = bytes(f'{json.dumps(msg)}\r\n', 'utf-8')
      print(f'send: {to_send}')

    else:
      packet.flow_configuration = self.flow_configuration
      packet.delay = self.trigger_configuration.delay
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

  def confirm_dynamic_profile(self):
    assert(self.dev)
    assert(isinstance(self.flow_configuration, DynamicFlow))

    lin_x = self.flow_configuration.time
    lin_y = self.flow_configuration.flow

    for x, y in zip(lin_x, lin_y):
      packet = ConfigurationPacket()
      packet.flow_configuration = DynamicFlowInterval(x, y)
      to_send = packet.toBytes()
      print(f'send: {to_send}')
      self.dev.write(to_send)
      time.sleep(0.005)

    packet = ConfigurationPacket()
    packet.flow_configuration = DynamicFlowInterval(max(lin_x) + 20, 0) 
    packet.fin = 1
    to_send = packet.toBytes()
    print(f'send: {to_send}')
    self.dev.write(to_send)
  
    self.processing_status = ProcessingStatus.WAITING_FOR_PROFILE_CONFIRMATION

  def send_dynamic_profile(self, *data: Optional[Any]):
    assert(self.dev)
    assert(isinstance(self.flow_configuration, DynamicFlow))

    packet = ConfigurationPacket()
    lin_x = self.flow_configuration.time
    lin_y = self.flow_configuration.flow
    interval = self.flow_configuration.interval
    flow_config = DynamicFlow(lin_x, lin_y, len(lin_x), max(lin_x) - min(lin_x), interval)
    packet.flow_configuration = flow_config
    to_send = packet.toBytes()
    print(f'send: {to_send}')
    self.dev.write(to_send)

    for x, y in zip(lin_x, lin_y):
      self.acknowledged[x] = { 'ack': False, 'flow': y }
      packet = ConfigurationPacket()
      packet.flow_configuration = DynamicFlowInterval(x, y)
      to_send = packet.toBytes()
      print(f'send: {to_send}')
      self.dev.write(to_send)
      time.sleep(0.005)

    packet = ConfigurationPacket()
    packet.flow_configuration = DynamicFlowInterval(max(lin_x) + interval, 0) 
    packet.fin = 1
    to_send = packet.toBytes()
    print(f'send: {to_send}')
    self.dev.write(to_send)
  
    self.processing_status = ProcessingStatus.WAITING_FOR_PROFILE_CONFIRMATION
  
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
        assert(self.dev)
        try:
          data = self.dev.readline()
          self.process_message(data)
        except Exception as e:
          self.error_count += 1
          self.call_cb(Callback.ON_CONNECTION_FAILURE, e)
      elif self.processing_status == ProcessingStatus.WAITING_FOR_FLOW:
        assert(self.dev)
        line = self.dev.readline()
        msg = line.rstrip().decode('utf-8')
        if len(msg) == 0: continue
        if msg[0] == 'f':
          # [ts, flow, motor, driver] = msg[2:].split(',')
          [ts, flow, driver] = msg[2:].split(',')
          # print(driver)
          # print(motor, driver)
          self.call_cb(Callback.ON_FLOW_DATA, int(ts), float(flow))
        if msg[0] == 'i' and msg != 'interval' and type(self.flow_configuration) == DynamicFlow:
          self.processing_status = ProcessingStatus.WAITING_FOR_PROFILE_CONFIRMATION
        elif msg == 'alive':
          self.processing_status = ProcessingStatus.WAITING_FOR_HEARTBEAT
        else:
          print(f'recv: {msg}')
      elif self.processing_status == ProcessingStatus.SENDING_DYNAMIC_PROFILE:
        self.send_dynamic_profile()
      elif self.processing_status == ProcessingStatus.WAITING_FOR_PROFILE_CONFIRMATION:
        assert(self.dev)
        assert(isinstance(self.flow_configuration, DynamicFlow))
        line = self.dev.readline()
        msg = line.rstrip().decode('utf-8')
        if msg[0] == 'i' and msg != 'interval':
          [pre_time, pre_flow] = msg.split(',')
          print(pre_time[1:], pre_flow[2:])
          parsed_time = int(pre_time[1:])
          parsed_flow = float(pre_flow[2:])
          t_idx = None
          t_flow = None
          try:
            t_idx = self.flow_configuration.time.index(parsed_time)
            t_flow = self.flow_configuration.flow[t_idx]
          except Exception as e:
            print(f'Dynamic profile error: {e}')
          if t_idx == None or t_flow == None:
            to_send = bytes(f'nak\r\n', 'utf-8')
            self.acknowledged[parsed_time]['ack'] = False 
            self.acknowledged[parsed_time]['actual'] = parsed_flow 
            print(f'send: {to_send}')
            self.dev.write(to_send)
          elif isclose(t_flow, parsed_flow, abs_tol=0.1):
            to_send = bytes(f'ack\r\n', 'utf-8')
            self.acknowledged[parsed_time]['ack'] = True
            print(f'send: {to_send}')
            self.dev.write(to_send)
          else:
            to_send = bytes(f'nak\r\n', 'utf-8')
            print(f'send: {to_send}')
            self.acknowledged[parsed_time]['ack'] = False 
            self.acknowledged[parsed_time]['actual'] = parsed_flow 
            self.dev.write(to_send)

      else:
        self.thread_state = ThreadState.SLEEPING 
        time.sleep(0.1)
      




simulator = Simulator()