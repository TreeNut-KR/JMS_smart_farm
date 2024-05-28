# 베이스 이미지로 Python 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일들을 컨테이너에 복사
COPY DB/sqlite_setup.py .

# sqlite_setup.py 스크립트 실행
CMD ["python", "DB.sqlite_setup.py"]
