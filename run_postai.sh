#!/bin/bash

# PostAI 로컬 서버 실행 스크립트

PROJECT_DIR="/Users/macbook/Desktop/자동화"
cd "$PROJECT_DIR"

echo "🚀 PostAI 시작 중..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Flask 웹사이트: http://localhost:8000"
echo "📍 Streamlit 앱: http://localhost:8501"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏳ 30초 후 자동으로 브라우저가 열립니다..."
echo ""

# Flask 실행 (백그라운드)
echo "🔧 Flask 서버 시작..."
python3 web/server.py > /tmp/flask.log 2>&1 &
FLASK_PID=$!

# 2초 대기
sleep 2

# Streamlit 실행 (백그라운드)
echo "🤖 Streamlit 앱 시작..."
streamlit run app.py --logger.level=error --client.showErrorDetails=false > /tmp/streamlit.log 2>&1 &
STREAMLIT_PID=$!

# 3초 대기
sleep 3

# 브라우저 열기
echo "🌐 브라우저 열기..."
open "http://localhost:8000"

sleep 3

echo ""
echo "✅ PostAI 시작 완료!"
echo ""
echo "📝 로그인 정보:"
echo "   ID: admin"
echo "   PW: admin123"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 종료하려면 이 터미널을 닫으세요"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 프로세스 유지
wait $FLASK_PID $STREAMLIT_PID
