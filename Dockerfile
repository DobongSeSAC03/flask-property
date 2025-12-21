FROM python:3.12

WORKDIR /app

# requirements.txt 복사 후 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 프로젝트 전체 복사
COPY . .


ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5050

# FLASK_APP을 run.py로 지정 (루트에 있다고 가정)
ENV FLASK_APP=run.py

# 컨테이너가 노출할 포트
EXPOSE 5050

CMD ["python", "run.py"]