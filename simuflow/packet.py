from dataclasses import dataclass
from simuflow.configuration import FlowConfiguration, ManualFlow, ConstantFlow
from typing import Optional
import json

@dataclass
class ConfigurationPacket:
    _flow_type: Optional[str] = None
    _duration: Optional[int] = None
    _delay: Optional[int] = None
    _flow: Optional[float] = None
    _motor_state: Optional[int] = None
    _motor: Optional[int] = None
    _driver: Optional[int] = None

    @property
    def flow_type(self) -> Optional[str]:
        return self._flow_type

    @flow_type.setter
    def flow_type(self, v: FlowConfiguration) -> None:
        if v == ManualFlow:
            self._flow_type = 'm'
        elif v == ConstantFlow:
            self._flow_type = 'c'
        else:
            raise ValueError(f'Unknown value for flow type: {v}')
        
    @property
    def duration(self) -> Optional[int]:
        return self._duration

    @duration.setter
    def duration(self, v: int) -> None:
        self._duration = v
    
    @property
    def delay(self) -> Optional[int]:
        return self._delay

    @delay.setter
    def delay(self, v: int) -> None:
        self._delay = v
        
    @property
    def flow(self) -> Optional[float]:
        return self._flow

    @flow.setter
    def flow(self, v: float) -> None:
        self._flow = v

    @property
    def motor_state(self) -> Optional[int]:
        return self._motor_state

    @motor_state.setter
    def motor_state(self, v: int) -> None:
        self._motor_state = v

    @property
    def driver(self) -> Optional[int]:
        return self._driver

    @driver.setter
    def driver(self, v: int) -> None:
        print(v)
        self._driver = v

    @property
    def motor(self) -> Optional[int]:
        return self._motor

    @motor.setter
    def motor(self, v: int) -> None:
        self._motor = v

    def toBytes(self):
        values = {}
        if self.flow_type != None: values['t'] = self.flow_type
        if self.flow != None: values['f'] = self.flow
        if self.motor != None: values['m'] = self.motor
        if self.driver != None: values['dv'] = self.driver
        if self.motor_state != None: values['ms'] = self.motor_state
        if self.delay != None: values['dl'] = self.delay
        if self.duration != None: values['d'] = self.duration

        json_vals = json.dumps(values)
        byte_vals = bytes(f'{json_vals}\r\n', 'utf-8')
        return byte_vals