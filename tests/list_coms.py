import sys
import glob
import serial
import os

if __name__ == '__main__':
  if os.name == 'nt':  # sys.platform == 'win32':
    from serial.tools.list_ports_windows import comports
  elif os.name == 'posix':
      from serial.tools.list_ports_posix import comports
  else:
      raise ImportError("Sorry: no implementation for your platform ('{}') available".format(os.name))
  iterator = comports()
  device = None
  for n, (port, desc, hwid) in enumerate(iterator, 1):
    print(f'n: {n}, port: {port}, desc: {desc}, hwid: {hwid}')