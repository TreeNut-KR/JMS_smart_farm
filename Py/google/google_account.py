from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from authlib.integrations.starlette_client import OAuth
import requests
from jose import jwt
import os

app = FastAPI()
templates = Jinja2Templates(directory="Py/google")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 환경 변수를 사용해 OAuth 클라이언트 설정
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    authorize_url=os.getenv("GOOGLE_AUTH_URI"),
    authorize_params=None,
    access_token_url=os.getenv("GOOGLE_TOKEN_URI"),
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=os.getenv("GOOGLE_REDIRECT_URIS"),
    client_kwargs={'scope': 'openid profile email'},
)

@app.get("/", response_class=HTMLResponse)
async def get_login_html(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login/google")
async def login_google():
    # Extract the redirect_uri from the environment variables
    redirect_uris = os.getenv('GOOGLE_REDIRECT_URIS')
    print(type(redirect_uris))
    # if not redirect_uris:
    #     raise HTTPException(status_code=500, detail="GOOGLE_REDIRECT_URIS 환경 변수가 설정되지 않았습니다.")
    redirect_uri = redirect_uris[0]

    # Use the environment variables to create the login URL
    return {
        "url": f"{os.getenv('GOOGLE_AUTH_URI')}?response_type=code&client_id={os.getenv('GOOGLE_CLIENT_ID')}&redirect_uri={redirect_uri}&scope=openid%20profile%20email&access_type=offline"
    }


@app.get("/auth/google")
async def auth_google(code: str):
    # 환경 변수를 사용하여 토큰 URL 및 데이터 설정
    token_url = os.getenv("GOOGLE_TOKEN_URI")
    data = {
        "code": code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URIS").split(',')[0],  # 여기도 수정
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
    return user_info.json()

@app.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    # JWT 토큰 디코딩 시, GOOGLE_CLIENT_SECRET 환경 변수를 사용
    return jwt.decode(token, os.getenv("GOOGLE_CLIENT_SECRET"), algorithms=["HS256"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
