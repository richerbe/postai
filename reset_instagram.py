#!/usr/bin/env python3
"""
인스타그램 세션 초기화 및 업로드 테스트
터미널에서 직접 실행: python3 reset_instagram.py
"""
import os, sys, time
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PIL import Image
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, TwoFactorRequired

USERNAME = "geumseok_jewellery"
PASSWORD = "!asdf5091j5"
SESSION_FILE = "instagram_session.json"
TEST_IMAGE = "assets/images/jewellery_1080.jpg"

print("=" * 50)
print("인스타그램 세션 초기화 및 테스트")
print("=" * 50)

# 1. 세션 파일 삭제
if Path(SESSION_FILE).exists():
    os.remove(SESSION_FILE)
    print("✓ 기존 세션 삭제")

# 2. 테스트 이미지 준비
Path("assets/images").mkdir(parents=True, exist_ok=True)
if not Path(TEST_IMAGE).exists():
    img = Image.new("RGB", (1080, 1080), color=(255, 215, 0))
    img.save(TEST_IMAGE, "JPEG", quality=90)
print(f"✓ 테스트 이미지: {TEST_IMAGE}")

# 3. 새로 로그인
print("\n로그인 중...")
cl = Client()
cl.delay_range = [2, 4]

try:
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings(SESSION_FILE)
    info = cl.account_info()
    print(f"✓ 로그인 성공: @{info.username}")
except TwoFactorRequired:
    code = input("2단계 인증 코드 입력: ")
    cl.login(USERNAME, PASSWORD, verification_code=code)
    cl.dump_settings(SESSION_FILE)
    print("✓ 2단계 인증 완료")
except ChallengeRequired:
    print("⚠️  보안 인증 필요!")
    print("인스타그램 앱에서 로그인 허용 후 다시 실행하세요.")
    sys.exit(1)
except Exception as e:
    print(f"✗ 로그인 실패: {e}")
    sys.exit(1)

# 4. 업로드 테스트
print("\n업로드 테스트 중...")
time.sleep(2)

try:
    media = cl.photo_upload(
        Path(TEST_IMAGE),
        caption="테스트 포스트 - 금석 쥬얼리 자동화 테스트 💍 #금석쥬얼리",
        configure_timeout=15,
    )
    print(f"✓ 업로드 성공!")
    print(f"  URL: https://www.instagram.com/p/{media.code}/")

except Exception as e:
    print(f"✗ 업로드 실패: {type(e).__name__}: {e}")
    print("\n해결 방법:")
    print("1. 인스타그램 앱에서 계정에 이상이 없는지 확인")
    print("2. VPN 사용 중이라면 끄고 재시도")
    print("3. 인스타그램 앱 → 설정 → 보안 → 로그인 활동 확인")
