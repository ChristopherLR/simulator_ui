from enum import Enum, auto
import threading
import json
import socket

class ConnectionStatus(Enum):
  CONNECTED = auto()
  DISCONNECTED = auto()

class ProcessingStatus(Enum):
  WAITING_FOR_CONNECTION = auto()
  WAITING_FOR_HEARTBEAT = auto()
  WAITING_FOR_FLOW = auto()


class Simulator(threading.Thread):

  def __init__(self):
    threading.Thread.__init__(self, daemon=True)

    self.connection_status = ConnectionStatus.DISCONNECTED
    self.processing_status = ProcessingStatus.WAITING_FOR_CONNECTION
    self.address = None
    self.dev = None
    self.on_success_callback = self.on_success
    self.on_failure_callback = self.on_failure

  def on_success(self):
    print("Connection Successful")

  def on_failure(self, msgs):
    print(f"Connection Failed: {msgs}")

  def connect(self, address, on_failure, on_success):
    self.on_success_callback = on_success
    self.on_failure_callback = on_failure
    self.address = address
    print(f'Attempting connection: {address}')
    self.start()

  def try_connection(self):
      errors = []
      s = None
      try:
        for res in socket.getaddrinfo(self.address, 2000, socket.AF_INET, socket.SOCK_STREAM):
          af, socktype, proto, canonname, sa = res
          try:
            s = socket.socket(af, socktype, proto)
          except Exception as msg:
            s = None
            errors.append(msg)
            continue
          try:
            s.connect(sa)
          except Exception as msg:
            s.close()
            s = None
            errors.append(msg)
            continue
          break
      except Exception as msg:
        errors.append(msg)

      if s is None:
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.on_failure_callback(errors)
      else:
        self.connection_status = ConnectionStatus.CONNECTED
        self.processing_status = ProcessingStatus.WAITING_FOR_HEARTBEAT
        self.on_success_callback()
        self.socket = s

  def run(self):

    if self.connection_status == ConnectionStatus.DISCONNECTED:
      self.try_connection()

    while True:
      if self.processing_status == ProcessingStatus.WAITING_FOR_HEARTBEAT:
        data = self.socket.recv(1024)
        print(data)
      else:
        break
      




simulator = Simulator()