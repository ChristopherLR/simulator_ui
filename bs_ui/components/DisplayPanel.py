from PySide6.QtWidgets import ( 
  QVBoxLayout, QFrame, QWidget, QPushButton, QLabel, QFileDialog,
)
from PySide6.QtCore import QSize, Qt, QDir, QObject

from bs_ui.components.Graph import Canvas 
from bs_ui.devices.simulator import simulator

class DisplayPanel(QFrame):
  def __init__(self, parent):
    super(DisplayPanel, self).__init__(parent)
    self.setObjectName('DisplayPanel')
    self.setStyleSheet("""
      #DisplayPanel { 
        margin:0px; 
        border:1px solid black; 
        min-width: 350px;
      }
    """)

    label = QLabel(self)
    label.setText('Output')
    label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
    
    self.layout = QVBoxLayout(self)

    graph = Canvas(self)
    graph.setFixedHeight(250)
    simulator.on_flow_callback = graph.update_data
    simulator.add_simulation_start_callback(graph.clear_data)
    self.graph = graph

    self.layout.addWidget(label)
    self.layout.addWidget(graph)

    self.button = QPushButton("Export")
    self.button.clicked.connect(self.export)

    self.layout.addWidget(self.button)

  def export(self):
    (file_name, _) = QFileDialog.getSaveFileName(caption="Save CSV")
    # TODO: better handling here
    if file_name == "": return
    print(file_name)

    if file_name.endswith(".csv") == False:
      file_name = f'{file_name}.csv'

    (xdata, ydata) = self.graph.get_data()
    with open(file_name, 'w') as f:
      f.write("time(ms),flow(l/min)\n")
      for (x, y) in zip(xdata, ydata):
        f.write(f'{x},{y}\n')