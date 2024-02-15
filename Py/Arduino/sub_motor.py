import serial
import time

# 시리얼 포트 설정. COM포트와 보레이트는 실제 환경에 맞게 수정해야 합니다.
ser = serial.Serial('COM3', 9600)

def turn_on_servo():
    # 'ON' 명령을 전송합니다. 명령 형식은 실제 서보 모터 제어 방식에 따라 다를 수 있습니다.
    ser.write(b'ON\n')

def turn_off_servo():
    # 'OFF' 명령을 전송합니다. 명령 형식은 실제 서보 모터 제어 방식에 따라 다를 수 있습니다.
    ser.write(b'OFF\n')

# 서보 모터를 켜고 2초 후에 끕니다.
while 1:
    turn_on_servo()


# 시리얼 통신 종료
ser.close()
