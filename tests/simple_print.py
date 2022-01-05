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

device = serial.Serial('/dev/tty.usbmodem111401', 115200)

fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [], 'b')

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
      [ts, flow] = msg[2:].split(',')
      # print(flow)
      update_data(x=int(ts), y=float(flow))


def exit_handler(signum, frame):
  os.kill(os.getpid(), signal.SIGUSR1)
  if device.is_open:
    device.close()
  sys.exit(0)

def run():
  signal.signal(signal.SIGINT, exit_handler)
  x = threading.Thread(target=listen, daemon=True)
  x.start()

  
  msg = { 'type': 'connect', 'version': '0.1.0' }
  to_send = bytes(f'{json.dumps(msg)}\r\n', 'utf-8')
  print(f'send: {to_send}')
  device.write(to_send)
  time.sleep(3)

  start_flow = { 'type': 'const', 'delay': 1500, 'flow': 25.0, 'length': 3000 }
  to_send = bytes(f'{json.dumps(start_flow)}\r\n', 'utf-8')
  print(f'send: {to_send}')
  device.write(to_send)

  def init():
      ax.set_xlim(0, 10000)
      ax.set_ylim(0, 200)
      return ln,

  ani = FuncAnimation(fig, update, init_func=init, blit=True, interval=10)

  plt.show()




if __name__ == '__main__':
    run()
