# 빌드 스테이지
FROM python:3.11.5-slim-bullseye AS builder

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치 및 pip 업그레이드
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 실행 스테이지
FROM python:3.11.5-slim-bullseye

# 시간대 설정을 위한 환경 변수
ENV TZ=Asia/Seoul

# 시스템 패키지 설치 및 시간대 설정
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    && pip install --no-cache-dir pymysql cryptography

# 작업 디렉토리 설정
WORKDIR /app

# 빌드 스테이지에서 설치된 Python 패키지 복사
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 애플리케이션 파일 복사
COPY .. .

# 비루트 사용자 생성 및 권한 설정
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 기본 명령
CMD ["python", "main.py"]