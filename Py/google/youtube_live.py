import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
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
            "javascript_origins":os.getenv("GOOGLE_JAVASCRIPT_ORIGINS")
        }
    }
    return client_secrets

# OAuth 2.0을 위한 스코프 설정
SCOPES = ['https://www.googleapis.com/auth/youtube']

# API 정보
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
    client_secrets = get_client_secrets()
    flow = InstalledAppFlow.from_client_config(client_secrets, SCOPES)
    credentials = flow.run_local_server()
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def create_live_event(youtube, title, description, start_time, end_time):
    insert_broadcast_response = youtube.liveBroadcasts().insert(
        part="snippet,status",
        body=dict(
            snippet=dict(
                title=title,
                description=description,
                scheduledStartTime=start_time,
                scheduledEndTime=end_time
            ),
            status=dict(
                privacyStatus="private"
            )
        )
    ).execute()

    snippet = insert_broadcast_response["snippet"]

    broadcast_id = insert_broadcast_response["id"]
    print("방송 ID: %s" % broadcast_id)
    print("방송 제목: %s" % snippet["title"])
    print("예정된 시작 시간: %s" % snippet["scheduledStartTime"])
    print("예정된 종료 시간: %s" % snippet["scheduledEndTime"])

    # 생성된 라이브 이벤트의 URL을 구성
    live_event_url = f"https://www.youtube.com/watch?v={broadcast_id}"
    print("라이브 이벤트 URL: %s" % live_event_url)

if __name__ == "__main__":
    youtube = get_authenticated_service()
    try:
        create_live_event(youtube,
                          "JMS Smart Farm Live",
                          "이것은 테스트 라이브 이벤트입니다.",
                          datetime.timedelta(),
                          datetime.timedelta(hours=12))
    except HttpError as e:
        print("HTTP 에러 %d 발생:/n%s" % (e.resp.status, e.content))