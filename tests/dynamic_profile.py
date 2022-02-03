import serial
import os
import signal
import sys
import time
import json
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
from pathlib import Path
from os import listdir
from os.path import isfile, join
from simuflow import read_inhalation_profile, __version__
from simuflow.packet import ConfigurationPacket
from simuflow.configuration import *

device = serial.Serial('/dev/tty.usbmodem114401', 115200)
lin_x, lin_y = read_inhalation_profile('inhalation_profiles/40_6.csv', 20)

fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [], 'b', label = 'response')
plt.plot(lin_x, lin_y, label = 'input')
plt.legend()

def update_data(x, y):
  xdata.append(x)
  ydata.append(y)
  # ln.set_data(xdata, ydata)
  # return ln,


def update(frame):
    ln.set_data(xdata, ydata)
    return ln,


def listen():
  while True:
    line = device.readline()
    msg = line.rstrip().decode('utf-8')
    print(msg)
    if msg[0] == 'f':
      [ts, flow, driver] = msg[2:].split(',')
      # print(flow)
      update_data(x=int(ts), y=float(flow))

    if msg[0] == 'i' and msg != 'interval':
      [pre_time, pre_flow] = msg.split(',')
      print(pre_time[1:], pre_flow[2:])
      parsed_time = int(pre_time[1:])
      parsed_flow = float(pre_flow[2:])
      t_idx = lin_x.index(parsed_time)
      t_flow = lin_y[t_idx]
      if round(t_flow, 2) == parsed_flow:
        to_send = bytes(f'ack\r\n', 'utf-8')
        print(f'send: {to_send}')
        device.write(to_send)
      else:
        to_send = bytes(f'nak\r\n', 'utf-8')
        print(f'send: {to_send}')
        device.write(to_send)




def exit_handler(signum, frame):
  os.kill(os.getpid(), signal.SIGUSR1)
  if device.is_open:
    device.close()

  sys.exit(0)

def run():
  signal.signal(signal.SIGINT, exit_handler)
  x = threading.Thread(target=listen, daemon=True)
  x.start()

  
  msg = { 't': 'connect', 'version': __version__ }
  to_send = bytes(f'{json.dumps(msg)}\r\n', 'utf-8')
  print(f'send: {to_send}')
  device.write(to_send)
  time.sleep(1)

  packet = ConfigurationPacket()
  flow_config = DynamicFlow(lin_x, lin_y, len(lin_x), max(lin_x) - min(lin_x), 20)
  packet.flow_configuration = flow_config
  to_send = packet.toBytes()
  print(f'send: {to_send}')
  device.write(to_send)

  for x, y in zip(lin_x, lin_y):
    packet = ConfigurationPacket()
    packet.flow_configuration = DynamicFlowInterval(x, y)
    to_send = packet.toBytes()
    print(f'send: {to_send}')
    device.write(to_send)
    time.sleep(0.003)

  packet = ConfigurationPacket()
  packet.flow_configuration = DynamicFlowInterval(max(lin_x) + 20, 0) 
  packet.fin = 1
  to_send = packet.toBytes()
  print(f'send: {to_send}')
  device.write(to_send)
  time.sleep(1)

  msg = { 't': 'run' }
  to_send = bytes(f'{json.dumps(msg)}\r\n', 'utf-8')
  print(f'send: {to_send}')
  device.write(to_send)


  def init():
      # ax.set_xlim(0, 10000)
      # ax.set_ylim(0, 200)
      return ln,

  ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=10)

  plt.show()




if __name__ == '__main__':
    run()
