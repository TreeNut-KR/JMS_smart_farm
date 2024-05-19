import serial.tools.list_ports
# from pygrabber.dshow_graph import FilterGraph
import subprocess
import re
from typing import Union
class device_data:
    def ar_get(self, mod: str) -> Union[str, None]:
        '''
        Arduino 데이터
        '''
        ports = serial.tools.list_ports.comports()
        for port_get, _, _ in sorted(ports):
            if mod in port_get:
                return port_get
        return None
    
    # def cam_get(self, mod: str) -> Union[int, None]:
    #     '''
    #     카메라 USB 데이터 (윈도우용)
    #     '''
    #     for device_index, device_name in enumerate(FilterGraph().get_input_devices()):
    #         if mod in device_name:
    #             return device_index
    #         else:
    #             return None

    def cam_get(self, mod: str) -> Union[int, None]:
        '''
        연결된 비디오 데이터 (리눅스용)
        '''
        command = "v4l2-ctl --list-devices"
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
        
        # 결과 문자열 전체에서 카메라 이름과 /dev/videoX 형식의 경로를 찾음
        pattern = rf'({mod}.*?)(/dev/video\d+)'
        matches = re.findall(pattern, result.stdout, re.DOTALL)
        
        if matches:
            # 첫 번째 매치의 두 번째 그룹(/dev/videoX)에서 숫자만 추출
            device_path = matches[0][1]
            index = int(''.join(filter(str.isdigit, device_path)))
            return index
        return None
    
if __name__ == "__main__":
    df = device_data()
    port = df.ar_get("USB")
    print(port)