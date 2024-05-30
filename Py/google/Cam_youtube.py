import cv2
import os
from dotenv import load_dotenv
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import pytz
from datetime import datetime, timedelta

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 인증 정보 가져오기
def get_client_secrets():
    client_secrets = {
        "installed": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "project_id": os.getenv("GOOGLE_PROJECT_ID"),
            "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
            "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": os.getenv("GOOGLE_REDIRECT_URIS"),
            "javascript_origins": os.getenv("GOOGLE_JAVASCRIPT_ORIGINS")
        }
    }
    return client_secrets

# YouTube API 인증 설정
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
client_secrets = get_client_secrets()

flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
    client_secrets, scopes)
credentials = flow.run_local_server(port=0)

youtube = googleapiclient.discovery.build(
    "youtube", "v3", credentials=credentials)

# 웹캠 캡처 설정
cap = cv2.VideoCapture(0)

# 라이브 방송 예약 함수
def schedule_live_stream():
    seoul_timezone = pytz.timezone('Asia/Seoul')
    current_time_seoul = datetime.now(seoul_timezone)
    start_time_str = current_time_seoul.strftime('%Y-%m-%dT%H:%M:%SZ')

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": "My Webcam Video",
                "description": "This is a video from my webcam.",
                "tags": ["webcam", "python"]
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body="webcam_video.mp4"
    )
    response = request.execute()
    print("Video uploaded:", response["id"])
    return response["id"]


# 라이브 방송 시작
def start_live_stream(broadcast_id):
    request = youtube.liveBroadcasts().transition(
        broadcastStatus="live",
        id=broadcast_id,
        part="id,status"
    )
    response = request.execute()
    print("Live stream started:", response["id"])

# 메인 루프
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('webcam_video.mp4', fourcc, 30.0, (640, 480))

while True:
    ret, frame = cap.read()
    out.write(frame)
    cv2.imshow("Live Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

out.release()
cap.release()
cv2.destroyAllWindows()

broadcast_id = schedule_live_stream()
