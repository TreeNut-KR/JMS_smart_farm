from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from fastapi.templating import Jinja2Templates
import cv2
import numpy as np
import asyncio
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="Py/google")

@app.get("/", response_class=HTMLResponse)
async def get_login_html(request: Request):
    return templates.TemplateResponse("live.html", {"request": request})

class TestVideoStreamTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()  # VideoStreamTrack의 생성자 호출
        self.counter = 0

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        
        # 테스트 패턴 생성 (여기서는 단순한 색상 변화)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:, :] = (self.counter % 255, 0, 0)
        self.counter += 1
        
        # OpenCV를 사용하여 numpy 배열을 aiortc가 이해할 수 있는 Frame으로 변환
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

# 웹소켓 연결을 위한 핸들러 내에서 미디어 트랙 추가 부분 수정
@app.websocket("/stream")
async def handle_stream(websocket: WebSocket):
    await websocket.accept()

    pc = RTCPeerConnection()

    # 수정된 부분: TestVideoStreamTrack 인스턴스를 생성하여 추가
    video_track = TestVideoStreamTrack()
    pc.addTrack(video_track)

    # 제공할 SDP 생성
    offer = await pc.createOffer()  # 수정된 부분
    await pc.setLocalDescription(offer)

    # 클라이언트에게 제공할 SDP 전송
    try:
        await websocket.send_json({"sdp": pc.localDescription.sdp})
    except websocket.exceptions.ConnectionClosedOK:
        print("WebSocket 연결이 정상적으로 종료되었습니다.")


    # 클라이언트로부터 SDP 응답 받기
    response = await websocket.receive_json()
    await pc.setRemoteDescription(RTCSessionDescription(
        type="answer", sdp=response["sdp"]))

    # 연결 유지 및 데이터 전송
    while True:
        await asyncio.sleep(1)
        # 필요에 따라 데이터 전송 로직 추가

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
