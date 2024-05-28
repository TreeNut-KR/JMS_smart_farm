# Python 이미지를 기반으로 설정
FROM python:3.12.1

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 어플리케이션 실행
CMD ["uvicorn", "API.complexed_chart:app", "--host", "0.0.0.0", "--port", "8000"]