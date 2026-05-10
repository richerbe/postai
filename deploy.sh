#!/bin/bash

# 배포 전 체크리스트
echo "🚀 SNS 자동화 앱 배포 시작..."
echo ""

# 1. 환경변수 확인
if [ ! -f .env ]; then
    echo "❌ .env 파일이 없습니다!"
    echo "📝 .env.example을 참고하여 .env 파일을 생성하세요."
    exit 1
fi

echo "✅ .env 파일 확인 완료"

# 2. 의존성 설치
echo "📦 Python 의존성 설치 중..."
pip install -r requirements.txt -q
echo "✅ 의존성 설치 완료"

# 3. 데이터베이스 초기화
echo "🗄️ 데이터베이스 초기화 중..."
python -c "from web.server import init_db; init_db()"
echo "✅ 데이터베이스 준비 완료"

# 4. Streamlit 앱 테스트
echo "🧪 Streamlit 앱 문법 검사 중..."
python -m py_compile app.py
if [ $? -eq 0 ]; then
    echo "✅ Streamlit 앱 검사 완료"
else
    echo "❌ Streamlit 앱에 오류가 있습니다!"
    exit 1
fi

# 5. Flask 앱 테스트
echo "🧪 Flask 앱 문법 검사 중..."
python -m py_compile web/server.py
if [ $? -eq 0 ]; then
    echo "✅ Flask 앱 검사 완료"
else
    echo "❌ Flask 앱에 오류가 있습니다!"
    exit 1
fi

echo ""
echo "📋 배포 전 체크리스트:"
echo "  ✅ .env 파일 설정됨"
echo "  ✅ 의존성 설치됨"
echo "  ✅ 데이터베이스 준비됨"
echo "  ✅ 코드 검사 완료"
echo ""

# Docker 배포 옵션
read -p "Docker로 배포하시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🐳 Docker 이미지 빌드 중..."
    docker-compose build
    echo "✅ Docker 이미지 빌드 완료"

    echo "🚀 Docker 컨테이너 시작 중..."
    docker-compose up -d
    echo "✅ Docker 배포 완료!"
    echo ""
    echo "📍 접속 주소:"
    echo "  🌐 Flask 웹: http://localhost:8000"
    echo "  🤖 Streamlit: http://localhost:8501"
else
    echo "📍 수동 실행 명령어:"
    echo ""
    echo "터미널 1 (Flask):"
    echo "  cd web && python -m flask run --host=0.0.0.0 --port=8000"
    echo ""
    echo "터미널 2 (Streamlit):"
    echo "  python -m streamlit run app.py --server.port=8501"
fi

echo ""
echo "✨ 배포 준비 완료!"
