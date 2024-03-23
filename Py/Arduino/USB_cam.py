import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
import uvicorn

from device import device_data

class Cam_server(device_data):
    def __init__(self) -> None:
        super().__init__()
        # 카메라 연결
        self.port = self.cam_get("60")
        self.camera = cv2.VideoCapture(self.port)

        # FastAPI 라우트 설정
        self.app = FastAPI()
        self.app.get("/")(self.index)
        self.app.get("/video_feed")(self.video_feed)

    def gen_frames(self):
        '''
        실시간으로 영상을 받은 후 ./video_feed으로 송출
        '''
        while True:
            success, frame = self.camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

    def index(self) -> HTMLResponse:
        '''
        HTML 형태의 문자열로 하이퍼링크를 포함하여 반환
        '''
        html_content = """
        <html>
            <head>
                <title>Security Camera Stream</title>
            </head>
            <body>
                <h1>Welcome to the security camera stream</h1>
                <p><a href="/video_feed">Live Video Feed</a></p>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    def video_feed(self) -> StreamingResponse:
        '''
        스트리밍 영상 전송
        '''
        return StreamingResponse(self.gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    # Cam 객체 생성 및 uvicorn 서버 실행
    cam = Cam_server()
    uvicorn.run(cam.app, port=8080, host='0.0.0.0')
