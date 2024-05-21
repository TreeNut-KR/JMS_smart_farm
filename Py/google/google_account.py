from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from authlib.integrations.starlette_client import OAuth
import requests
from jose import jwt
import os
import sqlite3
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="Py/google")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# OAuth 클라이언트 설정
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

# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('google_user.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_info (
        id TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        verified_email BOOLEAN NOT NULL,
        name TEXT NOT NULL,
        given_name TEXT NOT NULL,
        family_name TEXT NOT NULL,
        picture TEXT,
        locale TEXT
    )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.get("/", response_class=HTMLResponse)
async def get_login_html(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login/google")
async def login_google():
    redirect_uris = os.getenv('GOOGLE_REDIRECT_URIS').split(',')
    redirect_uri = redirect_uris[0]
    return {
        "url": f"{os.getenv('GOOGLE_AUTH_URI')}?response_type=code&client_id={os.getenv('GOOGLE_CLIENT_ID')}&redirect_uri={redirect_uri}&scope=openid%20profile%20email&access_type=offline"
    }

@app.get("/auth/google")
async def auth_google(code: str):
    token_url = os.getenv("GOOGLE_TOKEN_URI")
    data = {
        "code": code,
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": os.getenv("GOOGLE_REDIRECT_URIS").split(',')[0],
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch token")
    access_token = response.json().get("access_token")
    user_info_response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
    user_info = user_info_response.json()

    # 사용자 정보를 데이터베이스에 저장
    conn = sqlite3.connect('google_user.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO user_info (id, email, verified_email, name, given_name, family_name, picture, locale) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_info["id"],
        user_info["email"],
        user_info["verified_email"],
        user_info["name"],
        user_info["given_name"],
        user_info["family_name"],
        user_info["picture"],
        user_info["locale"]
    ))
    conn.commit()
    conn.close()

    return user_info

@app.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    return jwt.decode(token, os.getenv("GOOGLE_CLIENT_SECRET"), algorithms=["HS256"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
