
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from random import random 

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QSize

class Canvas(QFrame):
  def __init__(self, parent, xlim, ylim, plot_count = 1):
    super(Canvas, self).__init__(parent)

    dynamic_canvas = FigureCanvas(Figure(figsize=(5, 4)))
    self.layout = QVBoxLayout(self)

    self.xdata = []
    self.plot_count = plot_count
    self.create_data_map()


    self.axes = dynamic_canvas.figure.subplots()
    self.axes.set_xlim(0, xlim)
    self.axes.set_ylim(0, ylim)
    color_map = ['b', 'g', 'r', 'c', 'y']

    self.lines = []
    for i in range(self.plot_count):
      ln, = self.axes.plot([], [], color_map[i])
      self.lines.append(ln)

    self.timer = dynamic_canvas.new_timer(50)
    self.timer.add_callback(self.update_canvas)
    self.timer.start()

    self.layout.addWidget(dynamic_canvas)
  
  def create_data_map(self):
    self.ydata_map = []
    for i in range(self.plot_count):
      self.ydata_map.append([])


  def update_data(self, x, *y):
    self.xdata.append(x)
    for idx, ydata in enumerate(y):
      self.ydata_map[idx].append(ydata)

  def update_canvas(self):
    for i in range(self.plot_count):
      self.lines[i].set_data(self.xdata, self.ydata_map[i])
    self.lines[0].figure.canvas.draw()

  def clear_data(self):
    self.xdata.clear()
    self.ydata_map.clear()
    print(self.ydata_map)
    self.create_data_map()
    print(self.ydata_map)
    for i in range(self.plot_count):
      self.lines[i].set_data(self.xdata, self.ydata_map[i])
      self.lines[i].figure.canvas.draw()

  def get_data(self):
    return (self.xdata, self.ydata_map[0])

class Graph(QFrame):
  def __init__(self, parent=None, width=300, height=300):
    super(Graph, self).__init__(parent)

    self.fig = Canvas(width=5, height=4, dpi=100)
    
    inner = QFrame(self)
    inner.layout = QVBoxLayout(inner)
    inner.layout.addWidget(self.fig)

    self.layout = QHBoxLayout(self)
    self.layout.addWidget(inner)