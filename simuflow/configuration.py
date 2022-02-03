from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List
from simuflow import __version__

@dataclass
class SimulatorMetadata:
  simulator_version: str = 'unknown'
  ui_version: str = __version__

@dataclass
class FlowConfiguration(ABC):

  @abstractmethod
  def validate(self) -> bool:
    pass

@dataclass
class ConstantFlow(FlowConfiguration):
  flow: float = 0.0
  duration: int = 0

  def validate(self) -> bool:
    if self.duration <= 0: return False
    return True

@dataclass
class ManualFlow(FlowConfiguration):
  motor_state: int = 0
  driver: int = 0
  fan: int = 0

  def validate(self) -> bool:
    return True

@dataclass
class DynamicFlow(FlowConfiguration):
  time: List[int]
  flow: List[float]
  count: int = 0
  duration: int = 0
  interval: int = 0

  def validate(self) -> bool:
    return True

@dataclass
class DynamicFlowInterval(FlowConfiguration):
  interval: int 
  flow: float
  final: int = 0

  def validate(self) -> bool:
    return True

@dataclass
class DynamicProfileConfirmation(FlowConfiguration):

  def validate(self) -> bool:
    return True

@dataclass
class TriggerConfiguration():
  delay: int = 0