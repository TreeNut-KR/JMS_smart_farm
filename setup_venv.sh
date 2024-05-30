#!/bin/bash

# Python 설치 경로 설정
PYTHON_PATH="/usr/bin/python3.12"

# 가상 환경 디렉토리 이름 설정
ENV_DIR=".venv"

# pip 최신 버전으로 업그레이드
$PYTHON_PATH -m pip install --upgrade pip

# Python 3.12.1 가상 환경 생성
$PYTHON_PATH -m venv $ENV_DIR

echo "가상 환경 활성화 중..."
source $ENV_DIR/bin/activate

# pip 최신 버전으로 업그레이드 (가상 환경 내부)
pip install --upgrade pip

# requirements.txt 파일에 있는 모든 패키지 설치
pip install -r requirements.txt

# DB\sqlite_setup.py 스크립트 실행
echo "DB\sqlite_setup.py 스크립트를 실행 중..."
python DB/sqlite_setup.py

echo "가상 환경이 성공적으로 설정되었습니다."
echo "가상 환경을 활성화하려면 다음 명령을 사용하세요:"
echo "source $ENV_DIR/bin/activate"
