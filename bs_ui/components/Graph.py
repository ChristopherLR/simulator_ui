
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, QSize

class Canvas(QFrame):
  def __init__(self, parent):
    super(Canvas, self).__init__(parent)

    dynamic_canvas = FigureCanvas(Figure(figsize=(5, 4)))
    self.layout = QVBoxLayout(self)

    self.xdata = []
    self.ydata = []

    self.axes = dynamic_canvas.figure.subplots()
    self.axes.set_xlim(0, 10000)
    self.axes.set_ylim(0, 200)

    ln, = self.axes.plot([], [], 'b')
    self.line = ln
    self.timer = dynamic_canvas.new_timer(50)
    self.timer.add_callback(self.update_canvas)
    self.timer.start()

    self.layout.addWidget(dynamic_canvas)

  def update_data(self, x, y):
    self.xdata.append(x)
    self.ydata.append(y)

  def update_canvas(self):
    self.line.set_data(self.xdata, self.ydata)
    self.line.figure.canvas.draw()

  def clear_data(self):
    self.xdata = []
    self.ydata = []
    self.update_canvas()

  def get_data(self):
    return (self.xdata, self.ydata)

class Graph(QFrame):
  def __init__(self, parent=None, width=300, height=300):
    super(Graph, self).__init__(parent)

    self.fig = Canvas(width=5, height=4, dpi=100)
    
    inner = QFrame(self)
    inner.layout = QVBoxLayout(inner)
    inner.layout.addWidget(self.fig)

    self.layout = QHBoxLayout(self)
    self.layout.addWidget(inner)