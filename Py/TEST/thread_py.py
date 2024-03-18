import serial
import time
import threading

class T:
    def __init__(self) -> None:
        self.time_set = time.time()

    def read_from_arduino(self):
        while 1:
            if time.time() - self.time_set >= 1:#저장시간
                for i in [1,2,3,]:
                    print(f"{i}\n")
                self.time_set = time.time()

    def write_to_arduino(self):
        while True:
            try:
                command_1,command_2  = map(int, input("Enter command: ").split())  # 사용자 입력 받기
                print(f"input : {command_1, command_2}")
            except:
                pass


if __name__ == "__main__":
    t = T()
    # 데이터 읽기용 스레드
    read_thread = threading.Thread(target=t.read_from_arduino)
    read_thread.start()

    # 데이터 쓰기용 스레드
    write_thread = threading.Thread(target=t.write_to_arduino)
    write_thread.start()

    read_thread.join()
    write_thread.join()
