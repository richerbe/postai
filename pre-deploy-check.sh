#!/bin/bash

# 🚀 PostAI 배포 전 검증 스크립트
# 웹 및 모바일 앱이 배포 준비되었는지 확인

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🚀 PostAI 배포 전 검증                                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 체크 함수
check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Python 환경 확인
echo "📋 1. Python 환경 확인..."
if command -v python3 &> /dev/null; then
    check_pass "Python 설치됨"
else
    check_fail "Python 설치 필요"
fi

# 2. Node.js 확인
echo ""
echo "📋 2. Node.js 환경 확인..."
if command -v node &> /dev/null; then
    check_pass "Node.js 설치됨"
else
    check_fail "Node.js 설치 필요 (https://nodejs.org)"
fi

if command -v npm &> /dev/null; then
    check_pass "npm 설치됨"
fi

# 3. Git 확인
echo ""
echo "📋 3. Git 확인..."
if command -v git &> /dev/null; then
    check_pass "Git 설치됨"
else
    check_fail "Git 설치 필요"
fi

# 4. 웹 프로젝트 확인
echo ""
echo "📋 4. 웹 프로젝트 파일 확인..."
WEB_DIR="/Users/macbook/Desktop/자동화"
if [ -f "$WEB_DIR/app.py" ]; then
    check_pass "app.py 존재"
else
    check_fail "app.py 없음"
fi

if [ -f "$WEB_DIR/web/server.py" ]; then
    check_pass "web/server.py 존재"
else
    check_fail "web/server.py 없음"
fi

if [ -f "$WEB_DIR/requirements.txt" ]; then
    check_pass "requirements.txt 존재"
else
    check_fail "requirements.txt 없음"
fi

if [ -f "$WEB_DIR/.env" ]; then
    check_pass ".env 파일 존재"
else
    check_warn ".env 파일 없음 (배포 시 자동 생성됨)"
fi

# 5. 모바일 프로젝트 확인
echo ""
echo "📋 5. 모바일 프로젝트 파일 확인..."
MOBILE_DIR="/Users/macbook/Desktop/sns-mobile"
if [ -f "$MOBILE_DIR/app.json" ]; then
    check_pass "app.json 존재"
else
    check_fail "app.json 없음"
fi

if [ -f "$MOBILE_DIR/package.json" ]; then
    check_pass "package.json 존재"
else
    check_fail "package.json 없음"
fi

if [ -d "$MOBILE_DIR/app" ]; then
    check_pass "app 디렉토리 존재"
else
    check_fail "app 디렉토리 없음"
fi

if [ -f "$MOBILE_DIR/app/(auth)/login.tsx" ]; then
    check_pass "login.tsx 존재"
else
    check_fail "login.tsx 없음"
fi

# 6. Git 저장소 확인
echo ""
echo "📋 6. Git 저장소 상태..."
cd "$WEB_DIR"
if git rev-parse --git-dir > /dev/null 2>&1; then
    check_pass "웹 Git 저장소 초기화됨"
else
    check_fail "웹 Git 저장소 없음"
fi

cd "$MOBILE_DIR"
if git rev-parse --git-dir > /dev/null 2>&1; then
    check_pass "모바일 Git 저장소 초기화됨"
else
    check_fail "모바일 Git 저장소 없음"
fi

# 7. 배포 가이드 확인
echo ""
echo "📋 7. 배포 가이드 파일..."
cd "$WEB_DIR"
if [ -f "DEPLOYMENT_CHECKLIST.md" ]; then
    check_pass "DEPLOYMENT_CHECKLIST.md 존재"
fi

if [ -f "QUICK_START_DEPLOY.txt" ]; then
    check_pass "QUICK_START_DEPLOY.txt 존재"
fi

if [ -f "COMPLETE_DEPLOYMENT_GUIDE.md" ]; then
    check_pass "COMPLETE_DEPLOYMENT_GUIDE.md 존재"
fi

# 8. 필수 라이브러리 확인
echo ""
echo "📋 8. Python 라이브러리 확인..."
python3 -c "import flask" 2>/dev/null && check_pass "Flask 설치됨" || check_warn "Flask 미설치"
python3 -c "import streamlit" 2>/dev/null && check_pass "Streamlit 설치됨" || check_warn "Streamlit 미설치"
python3 -c "import yaml" 2>/dev/null && check_pass "PyYAML 설치됨" || check_warn "PyYAML 미설치"

# 최종 요약
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ 배포 전 검증 완료                                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 다음 단계:"
echo "1. DEPLOYMENT_CHECKLIST.md를 읽으세요"
echo "2. GitHub 계정을 생성하세요 (없으면)"
echo "3. 로컬에서 GitHub에 코드를 푸시하세요"
echo "4. Streamlit Cloud에 배포하세요"
echo "5. Railway에 배포하세요"
echo "6. 모바일 계정을 생성하세요 ($124)"
echo "7. iOS/Android를 빌드하고 배포하세요"
echo ""
echo "💡 팁: 배포 가이드를 차례대로 따르세요!"
echo ""
