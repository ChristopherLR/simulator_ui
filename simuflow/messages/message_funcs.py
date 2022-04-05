from simuflow.messages.flow_definition_pb2 import *

def send_proto(device, message):
  # print(f'sending: {message}')
  proto_data = message.SerializeToString()
  print(f'send: {proto_data}')
  proto_size = len(proto_data)
  # print(f'send size: {proto_size}')
  proto_end = '\n'
  to_send = (proto_size).to_bytes(1, byteorder='big') + proto_data + bytes(proto_end, 'utf-8')
  # print(f'send: {to_send}')
  device.write(to_send)


def send_const_flow(device, flow: float, duration: int):
  message = InterfaceMessage()
  message.message_type = InterfaceMessage.kConstantFlow
  message.constant_flow.flow = flow
  message.constant_flow.duration = duration

  send_proto(device, message)



def send_dynamic_flow(device, duration, count, interval):
  message = InterfaceMessage()
  message.message_type = InterfaceMessage.kDynamicFlow
  message.dynamic_flow.duration = duration
  message.dynamic_flow.count = count 
  message.dynamic_flow.interval = interval 

  send_proto(device, message)

def send_version_info(device, major, minor, patch):
  message = InterfaceMessage()
  message.message_type = InterfaceMessage.kVersionInfo
  message.version_info.major = major
  message.version_info.minor = minor
  message.version_info.patch = patch 

  send_proto(device, message)

def send_manual_flow(device, flow, driver, fan_direction):
  message = InterfaceMessage()
  message.message_type = InterfaceMessage.kManualFlow
  message.manual_flow.flow = flow 
  message.manual_flow.driver = driver 
  message.manual_flow.fan_direction = fan_direction

  send_proto(device, message)

def send_dynamic_flow_interval(device, interval, flow, final):
  message = InterfaceMessage()
  message.message_type = InterfaceMessage.kDynamicFlowInterval
  message.dynamic_flow_interval.interval = interval
  message.dynamic_flow_interval.flow = flow 
  message.dynamic_flow_interval.final = final

  send_proto(device, message)

def send_information_request(device, data_type):
  message = InterfaceMessage()
  message.message_type = InterfaceMessage.kInformationRequest
  message.information_request.data_type = data_type

  send_proto(device, message)