import serial.tools.list_ports
# from pygrabber.dshow_graph import FilterGraph
import subprocess
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
        
        # 결과 문자열을 줄 단위로 분리
        lines = result.stdout.split('\n')
        device_path = None
        
        # 카메라 이름이 나타나는 줄을 찾고, 그 다음 줄에서 디바이스 경로를 찾음
        for i, line in enumerate(lines):
            if mod in line:
                # 다음 줄(들)에서 /dev/videoX 형태의 경로 찾기
                for j in range(i+1, len(lines)):
                    if '/dev/video' in lines[j]:
                        device_path = lines[j].strip()
                        break
                break
        
        # 디바이스 경로에서 인덱스 추출
        if device_path:
            # 경로의 마지막 부분에서 숫자만 추출
            index = int(''.join(filter(str.isdigit, device_path)))
            return index
        return None
    
# if __name__ == "__main__":
#     df = device_data()
#     port = df.ar_get("USB")
#     print(port)