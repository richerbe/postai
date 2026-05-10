#!/bin/bash
# 소셜미디어 자동 업로드 시스템 초기 설정 스크립트

echo "=== 소셜미디어 자동 업로드 시스템 설치 ==="

# Python 버전 확인
python3 --version 2>/dev/null || { echo "Python3이 필요합니다."; exit 1; }

# 가상환경 생성
if [ ! -d "venv" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

# 패키지 설치
echo "패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# 필요한 디렉토리 생성
mkdir -p posts assets/images assets/videos

echo ""
echo "=== 설치 완료 ==="
echo ""
echo "다음 단계:"
echo "1. config.yaml 파일을 열어 API 키와 계정 정보 입력"
echo "2. source venv/bin/activate (가상환경 활성화)"
echo "3. python main.py new-post (포스트 템플릿 생성)"
echo "4. python main.py upload posts/example_post.yaml -p instagram -p threads"
echo ""
echo "도움말: python main.py --help"
