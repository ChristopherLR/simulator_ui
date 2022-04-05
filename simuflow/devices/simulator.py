from enum import Enum, auto
from re import I
import threading
import json
import time
from typing import Any, Optional
import serial
from simuflow.configuration import * 
from copy import copy
from math import isclose
from simuflow.messages.message_funcs import *
from simuflow.messages.flow_definition_pb2 import *

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
    try:
      send_version_info(dev, 0, 4, 0)
    except Exception as msg:
      self.processing_status = ProcessingStatus.WAITING_FOR_CONNECTION
      errors.append(msg)
      return 0

    (message, exception) = self.wait_for_message(dev)

    if exception != None:
      self.processing_status = ProcessingStatus.WAITING_FOR_CONNECTION
      errors.append(TimeoutError(42, "Timeout connecting to device"))
      return 0

    if message is None:
      return 0
    
    if message.message_type == SimulatorMessage.kVersionInfo:
      self.process_version_info(message)

    return 1


  def start_simulation(self):
    assert(self.dev)
    assert(self.flow_configuration)

    self.call_cb(Callback.ON_SIMULATION_START)
    message = InterfaceMessage()

    if isinstance(self.flow_configuration, DynamicFlow):
      for idx, k in enumerate(self.acknowledged):
        if self.acknowledged[k]['ack'] == False:
          print(k, self.acknowledged[k])
      message.message_type = InterfaceMessage.kRunDynamicFlowRequest
    elif isinstance(self.flow_configuration, ConstantFlow):
      message.message_type = InterfaceMessage.kConstantFlow
      message.constant_flow.flow = self.flow_configuration.flow
      message.constant_flow.duration = self.flow_configuration.duration
      message.constant_flow.trigger1_delay = self.trigger_configuration.delay
      message.constant_flow.trigger2_delay = self.trigger_configuration.delay
    elif isinstance(self.flow_configuration, ManualFlow):
      message.message_type = InterfaceMessage.kManualFlow
      message.manual_flow.driver = self.flow_configuration.driver
      message.manual_flow.motor_state = self.flow_configuration.motor_state
    elif isinstance(self.flow_configuration, DynamicFlowInterval):
      message.message_type = InterfaceMessage.kDynamicFlowInterval
      message.dynamic_flow_interval.interval = self.flow_configuration.interval
      message.dynamic_flow_interval.flow = self.flow_configuration.flow
      message.dynamic_flow_interval.final = self.flow_configuration.final
    elif isinstance(self.flow_configuration, DynamicProfileConfirmation):
      message.message_type = InterfaceMessage.kInformationRequest
      message.information_request.data_type = InformationRequest.DataType.kDynamicFlow

    error = False
    try:
      send_proto(self.dev, message)
    except Exception as e:
      print(f'Error writing to device: {e}')
      error = True

    del message 

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
      self.dev = dev
      self.processing_status = ProcessingStatus.WAITING_FOR_HEARTBEAT
      self.call_cb(Callback.ON_CONNECTION_SUCCESS, True)
      self.error_count = 0
      self.check_simulation_ready()

  def confirm_dynamic_profile(self):
    assert(self.dev)
    assert(isinstance(self.flow_configuration, DynamicFlow))

    lin_x = self.flow_configuration.time
    lin_y = self.flow_configuration.flow

    for x, y in zip(lin_x, lin_y):
      message = InterfaceMessage()
      message.message_type = InterfaceMessage.kDynamicFlowInterval
      message.dynamic_flow_interval.interval = x 
      message.dynamic_flow_interval.flow = y 
      send_proto(self.dev, message)
      time.sleep(0.0005)

    message = InterfaceMessage()
    message.message_type = InterfaceMessage.kDynamicFlowInterval
    message.dynamic_flow_interval.interval = max(lin_x) + 20
    message.dynamic_flow_interval.flow = 0
    message.dynamic_flow_interval.final = 1
    send_proto(self.dev, message)
  
    self.processing_status = ProcessingStatus.WAITING_FOR_PROFILE_CONFIRMATION

  def send_dynamic_profile(self, *data: Optional[Any]):
    assert(self.dev)
    assert(isinstance(self.flow_configuration, DynamicFlow))

    lin_x = self.flow_configuration.time
    lin_y = self.flow_configuration.flow
    interval = self.flow_configuration.interval

    message = InterfaceMessage()
    message.message_type = InterfaceMessage.kDynamicFlow
    message.dynamic_flow.duration = max(lin_x) - min(lin_x)
    message.dynamic_flow.interval = interval
    message.dynamic_flow.count = len(lin_x)

    send_proto(self.dev, message)

    message = InterfaceMessage()
    message.message_type = InterfaceMessage.kDynamicFlowInterval

    for x, y in zip(lin_x, lin_y):
      self.acknowledged[x] = { 'ack': False, 'flow': y }
      message.dynamic_flow_interval.interval = x
      message.dynamic_flow_interval.flow = y
      send_proto(self.dev, message)
      time.sleep(0.0005)

    message.dynamic_flow_interval.interval = max(lin_x) + interval
    message.dynamic_flow_interval.flow = 0
    message.dynamic_flow_interval.final = 1
    send_proto(self.dev, message)
  
    self.processing_status = ProcessingStatus.WAITING_FOR_PROFILE_CONFIRMATION
  
  def wait_for_message(self, dev=None):
    chosen = dev

    if dev == None:
      chosen = self.dev

    if chosen == None:
      print("No Device Connection")
      return

    size = 0

    try:
      size = chosen.read()
    except Exception as e:
      print(f'Error Reading Size: {e}')
      return (None, e)

    try:
      size = int.from_bytes(size, byteorder='big')
    except Exception as e:
      print(f'Error Converting Size: {e}')
      return (None, e)

    line = None
    try:
      line = chosen.read(size)
    except Exception as e:
      print(f'Error Reading Message: {e}')
      return (None, e)

    
    try:
      end = chosen.read()
    except Exception as e:
      print(f'Error Reading End: {e}')
      return (None, e)

    message = SimulatorMessage()

    try:
      message.ParseFromString(line)
    except Exception as e:
      print(f'Error Converting Message: {e}')
      return (None, e)

    print(message)
    return (message, None)

  def process_sim_message(self, message):
    print(message.message_type)
    if message.message_type == SimulatorMessage.MessageType.kVersionInfo:
      self.process_version_info(message)
    elif message.message_type == SimulatorMessage.MessageType.kFlow:
      self.process_flow(message)
    elif message.message_type == SimulatorMessage.MessageType.kError:
      self.process_error(message)
    elif message.message_type == SimulatorMessage.MessageType.kHeartbeat:
      self.process_heartbeat(message)
    elif message.message_type == SimulatorMessage.MessageType.kFlowInterval:
      self.process_flow_interval(message)
    else:
      return
  
  def process_version_info(self, message):
    print(f'process version info: {message}')
    version_info = message.version_info
    self.metadata.simulator_version = f"{version_info.major}.{version_info.minor}.{version_info.patch}"
    self.update_configuration(self.metadata)
    self.call_cb(Callback.ON_METADATA_UPDATE, self.metadata)
  
  def process_flow(self, message):
    ts = message.flow_info.timestamp
    flow = message.flow_info.timestamp
    self.call_cb(Callback.ON_FLOW_DATA, int(ts), float(flow))

  def process_error(self, message):
    print(message)

  def process_heartbeat(self, message):
    print(f'heartbeat received: {self.hb_count}\r', end = '')
    self.hb_count += 1
  
  def process_flow_interval(self, message):
    flow = message.flow_info.flow
    ts = message.flow_info.timestamp
    parsed_time = int(ts)
    parsed_flow = float(flow)
    t_idx = None
    t_flow = None

    ack_message = InterfaceMessage()
    nack_message = InterfaceMessage()
    ack_message.message_type = InterfaceMessage.kAck
    nack_message.message_type = InterfaceMessage.kNack

    try:
      t_idx = self.flow_configuration.time.index(parsed_time)
      t_flow = self.flow_configuration.flow[t_idx]
    except Exception as e:
      print(f'Dynamic profile error: {e}')
    if t_idx == None or t_flow == None:
      send_proto(self.dev, nack_message)
      self.acknowledged[parsed_time]['ack'] = False 
      self.acknowledged[parsed_time]['actual'] = parsed_flow 
    elif isclose(t_flow, parsed_flow, abs_tol=0.1):
      send_proto(self.dev, ack_message)
      self.acknowledged[parsed_time]['ack'] = True
    else:
      send_proto(self.dev, nack_message)
      self.acknowledged[parsed_time]['ack'] = False 
      self.acknowledged[parsed_time]['actual'] = parsed_flow 
    return


  def run(self):
    print('Sim thread running')
    while True:
      if self.error_count > 5:
        self.processing_status = ProcessingStatus.WAITING_FOR_CONNECTION
        self.error_count = 0
      elif self.processing_status == ProcessingStatus.ATTEMPTING_CONNECTION:
        err = self.try_connection()
        if err == -1: self.error_count += 1
      elif self.processing_status != None:
        (message, exception) = self.wait_for_message()
        if exception != None: print(exception)
        if message != None: self.process_sim_message(message)
      else:
        self.thread_state = ThreadState.SLEEPING 
        time.sleep(0.1)
      
simulator = Simulator()
