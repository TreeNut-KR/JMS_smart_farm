import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import threading
import uvicorn

class Cam:
    def __init__(self) -> None:
        # 카메라 연결
        self.camera = cv2.VideoCapture(1)
        self.app = FastAPI()

        # FastAPI 라우트 설정
        self.app.get("/")(self.index)
        self.app.get("/video_feed")(self.video_feed)

    def gen_frames(self):
        while True:
            success, frame = self.camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

    def index(self):
        return "Welcome to the security camera stream"

    def video_feed(self):
        return StreamingResponse(self.gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    # Cam 객체 생성 및 uvicorn 서버 실행
    cam = Cam()
    uvicorn.run(cam.app, host="192.168.45.29", port=8000)
