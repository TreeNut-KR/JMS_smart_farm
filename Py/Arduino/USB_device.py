import serial.tools.list_ports
from pygrabber.dshow_graph import FilterGraph
from typing import Union

class Usb:
    def __init__(self) -> None:
        self.port = None

    def usb_get(self, mod: str) -> Union[str, None]:
        ports = serial.tools.list_ports.comports()

        for port_get, desc, _ in sorted(ports):
            if mod in desc:
                self.port = port_get
                return self.port
        return None
    
    def cam_get(self, mod: str):
        for device_index, device_name in enumerate(FilterGraph().get_input_devices()):
            if mod in device_name:
                return device_index
            else:
                return 0