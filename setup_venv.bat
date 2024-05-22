@echo off
chcp 65001
SETLOCAL

:: Python 설치 경로 설정
SET PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe

:: 가상 환경 디렉토리 이름 설정
SET ENV_DIR=.venv

:: pip 최신 버전으로 업그레이드
"%PYTHON_PATH%" -m pip install --upgrade pip

:: Python 3.12.1 가상 환경 생성
"%PYTHON_PATH%" -m venv %ENV_DIR%

echo 가상 환경 활성화 중...
CALL %ENV_DIR%\Scripts\activate.bat

:: pip 최신 버전으로 업그레이드 (가상 환경 내부)
pip install --upgrade pip

:: requirements.txt 파일에 있는 모든 패키지 설치
pip install -r requirements.txt

echo 가상 환경이 성공적으로 설정되었습니다.
echo 가상 환경을 활성화하려면 다음 명령을 사용하세요:
echo CALL %ENV_DIR%\Scripts\activate.bat

ENDLOCAL
