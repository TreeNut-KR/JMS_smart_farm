import asyncio
import serial
import serial.tools.list_ports
from concurrent.futures import ThreadPoolExecutor

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print(f"{port}: {desc} [{hwid}]")

async def read_from_port_async(ser, loop):
    # ThreadPoolExecutor를 사용하여 비동기적으로 실행
    with ThreadPoolExecutor(1) as executor:
        while True:
            # run_in_executor를 사용하여 동기 함수를 비동기적으로 실행
            line = await loop.run_in_executor(executor, ser.readline)
            print("Data received:", line.decode('utf-8').rstrip())

async def main():
    # 시리얼 포트 나열
    list_serial_ports()
    
    # 시리얼 포트 설정
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    
    # 이벤트 루프 가져오기
    loop = asyncio.get_running_loop()
    
    # 비동기적으로 데이터 읽기
    await read_from_port_async(ser, loop)

if __name__ == "__main__":
    asyncio.run(main())
