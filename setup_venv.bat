@echo off
chcp 65001
SETLOCAL

SET INSTALLER_URL=https://www.python.org/ftp/python/3.12.1/python-3.12.1.exe
SET INSTALLER_PATH=%~dp0python-3.12.1.exe

echo Python 3.12.1 설치 파일 다운로드 중...
PowerShell -Command "(New-Object System.Net.WebClient).DownloadFile('%INSTALLER_URL%', '%INSTALLER_PATH%')"

echo Python 3.12.1 설치 중...
start /wait "" "%INSTALLER_PATH%" /quiet InstallAllUsers=1 PrependPath=1

echo 설치 완료

:: 가상 환경 디렉토리 이름 설정
SET ENV_DIR=.venv
python.exe -m pip install --upgrade pip
:: Python 3.12.1 가상 환경 생성
python -m venv %ENV_DIR%

echo 가상 환경 활성화 중...
CALL %ENV_DIR%\Scripts\activate.bat

:: pip 최신 버전으로 업그레이드
pip install --upgrade pip

:: requirements.txt 파일에 있는 모든 패키지 설치
pip install -r requirements.txt

echo 가상 환경이 성공적으로 설정되었습니다.
echo 가상 환경을 활성화하려면 다음 명령을 사용하세요:
echo CALL %ENV_DIR%\Scripts\activate.bat

ENDLOCAL
