from simuflow.messages.flow_definition_pb2 import ConstantFlow, InformationRequest, ManualFlow, InterfaceMessage 
import serial
import os
import signal
import threading
import time

device = serial.Serial("/dev/tty.usbmodem1401", 115200)
# device = serial.Serial('/dev/tty.usbmodem100927401', 115200)

def listen():
  while True:
    size = int.from_bytes(device.read(), byteorder='big')
    # print(f'recv size: {size}')
    line = device.read(size)
    print(f'recv: {line}')
    end = device.read()
    # print(f'recv end: {end}')
    try:
      message = InterfaceMessage()
      message.ParseFromString(line)
      print(message)
    except Exception as e:
      print(f'err: {e}')

    

def exit_handler(signum, frame):
  os.kill(os.getpid(), signal.SIGUSR1)
  if device.is_open: device.close()

def send_proto(message):
  # print(f'sending: {message}')
  proto_data = message.SerializeToString()
  print(f'send: {proto_data}')
  proto_size = len(proto_data)
  # print(f'send size: {proto_size}')
  proto_end = '\n'
  to_send = (proto_size).to_bytes(1, byteorder='big') + proto_data + bytes(proto_end, 'utf-8')
  # print(f'send: {to_send}')
  device.write(to_send)


def send_const_flow(flow: float, duration: int):
  message = InterfaceMessage()
  message.message_type = InterfaceMessage.kConstantFlow
  message.constant_flow.flow = flow
  message.constant_flow.duration = duration

  send_proto(message)



def send_dynamic_flow(duration, count, interval):
  message = InterfaceMessage()
  message.message_type = InterfaceMessage.kDynamicFlow
  message.dynamic_flow.duration = duration
  message.dynamic_flow.count = count 
  message.dynamic_flow.interval = interval 

  send_proto(message)

def send_version_info(major, minor, patch):
  message = InterfaceMessage()
  message.message_type = InterfaceMessage.kVersionInfo
  message.version_info.major = major
  message.version_info.minor = minor
  message.version_info.patch = patch 

  send_proto(message)

def send_manual_flow(flow, driver, fan_direction):
  message = InterfaceMessage()
  message.message_type = InterfaceMessage.kManualFlow
  message.manual_flow.flow = flow 
  message.manual_flow.driver = driver 
  message.manual_flow.fan_direction = fan_direction

  send_proto(message)

def send_dynamic_flow_interval(interval, flow, final):
  message = InterfaceMessage()
  message.message_type = InterfaceMessage.kDynamicFlowInterval
  message.dynamic_flow_interval.interval = interval
  message.dynamic_flow_interval.flow = flow 
  message.dynamic_flow_interval.final = final

  send_proto(message)

def send_information_request(data_type):
  message = InterfaceMessage()
  message.message_type = InterfaceMessage.kInformationRequest
  message.information_request.data_type = data_type

  send_proto(message)

      
def run():
  signal.signal(signal.SIGINT, exit_handler)
  x = threading.Thread(target=listen, daemon=True)
  x.start()

  delay = 0.000

  send_version_info(0, 4, 0)
  time.sleep(delay)
  send_const_flow(112.5, 5)
  time.sleep(delay)
  send_manual_flow(88.8, 10, ManualFlow.FanDirection.kClockwise)
  time.sleep(delay)
  send_dynamic_flow(100, 3200, 10)
  time.sleep(delay)
  send_dynamic_flow_interval(12300, 200.1212321, 0)
  time.sleep(delay)
  send_information_request(InformationRequest.kDynamicFlow)
  time.sleep(delay)

  input()

  # rec_message = InterfaceMessage()
  # rec_message.ParseFromString(proto_string)
  # print(rec_message)




if __name__ == '__main__':
  run()