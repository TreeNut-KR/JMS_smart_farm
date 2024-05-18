import serial
import time

# 시리얼 포트 설정
ser = serial.Serial('COM4', 9600, timeout=1)
time.sleep(2)  # 아두이노 리셋 후 통신을 위한 대기 시간

def send_and_receive(data):
    ser.write(data.encode())  # 데이터를 아두이노로 보냄
    time.sleep(0.1)  # 데이터 전송 및 처리를 위한 대기 시간
    if ser.inWaiting() > 0:  # 아두이노로부터 데이터를 받음
        received_data = ser.readline().decode().strip()  # 받은 데이터를 디코딩
        print("Received:", received_data)  # 받은 데이터 출력

try:
    while True:
        # 사용자로부터 데이터 입력 받음
        send_and_receive("1")  # 데이터 송수신 함수 호출

except KeyboardInterrupt:
    print("Program terminated")
finally:
    ser.close()  # 시리얼 포트 닫기
