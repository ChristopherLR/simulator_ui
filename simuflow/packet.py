from dataclasses import dataclass
from simuflow.configuration import *
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
    _fin: Optional[int] = None
    _interval: Optional[int] = None
    _count: Optional[int] = None

    @property
    def flow_configuration(self) -> Optional[str]:
        return self._flow_type

    @flow_configuration.setter
    def flow_configuration(self, v: FlowConfiguration):
        if type(v) == ManualFlow:
            self._flow_type = "manual"
            self.motor_state = v.motor_state
            self.driver = v.driver
            self.motor = v.fan
        elif type(v) == ConstantFlow:
            self._flow_type = "const"
            self.flow = v.flow
            self.duration = v.duration
        elif type(v) == DynamicFlow:
            self._flow_type = "dynamic"
            self.duration = int(v.duration)
            self.count = int(v.count)
            self.interval = int(v.interval)
        elif type(v) == DynamicFlowInterval:
            self._flow_type = "interval"
            self.interval = int(v.interval)
            self.flow = round(float(v.flow), 2)
        elif type(v) == DynamicProfileConfirmation:
            self._flow_type = "confirm"
        else:
            raise ValueError(f"Unknown value for flow type: {v}")

    @property
    def flow_type(self) -> Optional[str]:
        return self._flow_type

    @flow_type.setter
    def flow_type(self, v: FlowConfiguration) -> None:
        if v == ManualFlow:
            self._flow_type = "manual"
        elif v == ConstantFlow:
            self._flow_type = "const"
        elif v == DynamicFlow:
            self._flow_type = "dynamic"
        elif v == DynamicFlowInterval:
            self._flow_type = "interval"
        elif v == DynamicProfileConfirmation:
            self._flow_type = "confirm"
        else:
            raise ValueError(f"Unknown value for flow type: {v}")

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

    @property
    def fin(self) -> Optional[int]:
        return self._fin

    @fin.setter
    def fin(self, v: int) -> None:
        self._fin = int(v)

    @property
    def count(self) -> Optional[int]:
        return self._count

    @count.setter
    def count(self, v: int) -> None:
        self._count = v

    @property
    def interval(self) -> Optional[int]:
        return self._interval

    @interval.setter
    def interval(self, v: int) -> None:
        self._interval = v

    def toBytes(self):
        values = {}
        if self.flow_type != None: values["t"] = self.flow_type
        if self.flow != None: values["f"] = self.flow
        if self.motor != None: values["m"] = self.motor
        if self.driver != None: values["dv"] = self.driver
        if self.motor_state != None: values["ms"] = self.motor_state
        if self.delay != None: values["dl"] = self.delay
        if self.duration != None: values["d"] = self.duration
        if self.interval != None: values["dfi"] = self.interval
        if self.count != None: values["c"] = self.count
        if self.duration != None: values["d"] = self.duration
        if self.fin != None: values['fin'] = self.fin

        json_vals = json.dumps(values)
        byte_vals = bytes(f"{json_vals}\r\n", "utf-8")
        return byte_vals
