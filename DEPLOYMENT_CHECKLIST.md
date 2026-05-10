# 🚀 PostAI 배포 체크리스트 & 액션 플랜

**현재 시간**: 2026-05-10  
**프로젝트 상태**: ✅ 개발 완료, 배포 준비 완료

---

## 📋 배포 체크리스트

### PHASE 1: 웹 배포 (30분, 무료)

#### Step 1: GitHub 저장소 생성 및 코드 푸시
- [ ] GitHub 계정 없으면 생성 (https://github.com/signup)
- [ ] https://github.com/new 에서 새 저장소 생성
  - Repository name: `postai` (또는 원하는 이름)
  - Description: `SNS 자동화 플랫폼 - AI 기반 멀티채널 콘텐츠 관리`
  - Visibility: Public (배포용)
- [ ] 로컬에서 원격 저장소 추가:
  ```bash
  cd /Users/macbook/Desktop/자동화
  git remote add origin https://github.com/YOUR_USERNAME/postai.git
  git branch -M main
  git push -u origin main
  ```
- [ ] 모바일 앱도 별도 저장소로 푸시:
  ```bash
  cd /Users/macbook/Desktop/sns-mobile
  git remote add origin https://github.com/YOUR_USERNAME/postai-mobile.git
  git branch -M main
  git push -u origin main
  ```

#### Step 2: Streamlit Cloud 배포 (5분)
- [ ] https://streamlit.io/cloud 접속
- [ ] GitHub 계정으로 로그인
- [ ] "Create app" 클릭
  - Repository: `YOUR_USERNAME/postai`
  - Branch: `main`
  - Main file path: `app.py`
- [ ] 배포 완료 대기 (약 2-3분)
- [ ] URL 기록: `https://YOUR_USERNAME-postai.streamlit.app`

#### Step 3: Railway 배포 (5분)
- [ ] https://railway.app 접속
- [ ] GitHub 또는 계정으로 로그인
- [ ] "Create a new project" → "Deploy from GitHub repo"
- [ ] `postai` 저장소 선택
- [ ] 환경 변수 설정:
  ```
  FLASK_ENV=production
  SECRET_KEY=[암호 생성: python -c "import secrets; print(secrets.token_hex(32))"]
  DATABASE_URL=sqlite:///./postai.db
  ```
- [ ] 배포 완료 대기 (약 2-3분)
- [ ] 도메인 설정 (Custom domain 또는 기본값 사용)

#### Step 4: 웹 배포 검증
- [ ] Streamlit Cloud 접속: https://YOUR_USERNAME-postai.streamlit.app
  - [ ] 로그인 페이지 로드 ✓
  - [ ] 데모 계정(admin/admin123) 로그인 성공 ✓
  - [ ] 대시보드 모든 메뉴 로드 ✓
- [ ] Flask 웹사이트 접속: https://postai.up.railway.app
  - [ ] 랜딩 페이지 로드 ✓
  - [ ] 스크롤 애니메이션 작동 ✓
  - [ ] 버튼 호버 효과 작동 ✓

---

### PHASE 2: 모바일 배포 (1-3일, $124 초기)

**비용**: Apple Developer $99 + Google Play $25 = $124

#### Step 1: 필수 계정 생성

**Expo 계정** (무료)
- [ ] https://expo.dev 접속
- [ ] 계정 생성 (이메일 인증)
- [ ] `npx eas-cli` 설치:
  ```bash
  cd /Users/macbook/Desktop/sns-mobile
  npx eas-cli login
  # 이메일과 비밀번호로 로그인
  ```

**Apple Developer 계정** ($99/년)
- [ ] https://developer.apple.com/account 가입
- [ ] $99 결제
- [ ] iOS Bundle ID: `com.postai.mobile` 생성
- [ ] App Store Connect (https://appstoreconnect.apple.com)에서 앱 생성

**Google Play 계정** ($25 일회)
- [ ] https://play.google.com/console 가입
- [ ] $25 결제
- [ ] Android Package: `com.postai.mobile` 등록

#### Step 2: iOS 빌드 및 배포
- [ ] `eas.json` 존재 확인:
  ```bash
  cd /Users/macbook/Desktop/sns-mobile
  cat eas.json
  ```
- [ ] iOS 빌드 시작:
  ```bash
  eas build --platform ios
  ```
  - 대기 시간: 5-10분
  - 상태 모니터링: https://expo.dev/builds
- [ ] 빌드 완료 후 TestFlight에 제출:
  ```bash
  eas submit --platform ios
  ```
- [ ] App Store Connect에서 심사 상태 모니터링
  - 예상 시간: 1-3일
  - URL: https://appstoreconnect.apple.com

#### Step 3: Android 빌드 및 배포
- [ ] Android 빌드 시작:
  ```bash
  eas build --platform android
  ```
  - 대기 시간: 5-10분
  - 상태 모니터링: https://expo.dev/builds
- [ ] 빌드 완료 후 Play Store에 제출:
  ```bash
  eas submit --platform android
  ```
- [ ] Google Play Console에서 심사 상태 모니터링
  - 예상 시간: 1-3시간 (또는 수일)
  - URL: https://play.google.com/console

#### Step 4: 모바일 배포 검증
**iOS (TestFlight)**
- [ ] TestFlight 초대 수락
- [ ] iPhone에서 TestFlight 앱 설치
- [ ] PostAI 앱 설치
- [ ] 로그인 테스트 (admin/admin123) ✓
- [ ] 대시보드 네비게이션 ✓
- [ ] 버튼 터치 반응 ✓

**Android (Internal Testing)**
- [ ] Google Play Console → 내부 테스트 링크 수락
- [ ] Android 기기에서 앱 설치
- [ ] 로그인 테스트 (admin/admin123) ✓
- [ ] 대시보드 네비게이션 ✓
- [ ] 버튼 터치 반응 ✓

---

## 📊 배포 후 운영

### 모니터링
- [ ] Streamlit Cloud: 성능 및 에러 모니터링
- [ ] Railway: 로그 확인, 자동 스케일링 설정
- [ ] App Store: 리뷰 및 평점 모니터링
- [ ] Play Store: 리뷰 및 충돌 보고 확인

### 업데이트
```bash
# 버전 업데이트 (package.json / app.json)
npm version patch  # 1.0.0 → 1.0.1

# 웹 업데이트 (자동 배포)
git add -A
git commit -m "Update: [설명]"
git push origin main

# 모바일 업데이트
eas build --platform all --auto-submit
eas submit --platform all
```

---

## 🎯 예상 타임라인

| 단계 | 시간 | 상태 |
|------|------|------|
| GitHub 푸시 | 5분 | 즉시 |
| Streamlit 배포 | 5분 | 즉시 |
| Railway 배포 | 5분 | 즉시 |
| **웹 배포 완료** | **15-30분** | **완료** |
| 계정 생성 | 10분 | 비용 필요 ($124) |
| iOS 빌드 | 10분 | 자동 |
| iOS 심사 | 1-3일 | Apple 처리 |
| Android 빌드 | 10분 | 자동 |
| Android 심사 | 1-3시간 | Google 처리 |
| **모바일 배포 완료** | **1-3일** | **완료** |

---

## 🔑 중요 정보

### 로그인 자격증명
- **Streamlit 데모**: admin / admin123
- **Flask 웹**: 회원가입 후 admin 승인 필요

### API 엔드포인트
- **Flask (웹)**: https://postai.up.railway.app
- **Streamlit (앱)**: https://YOUR_USERNAME-postai.streamlit.app
- **모바일 (iOS)**: App Store → PostAI
- **모바일 (Android)**: Play Store → PostAI

### 필수 환경 변수
```
FLASK_ENV=production
SECRET_KEY=[자동 생성됨]
DATABASE_URL=sqlite:///./postai.db
STREAMLIT_SERVER_PORT=8501
```

---

## ⚠️ 문제 해결

### Streamlit 배포 실패
```bash
# 로컬에서 먼저 테스트
streamlit run app.py

# 파일 체크
ls -la .streamlit/config.toml
ls -la requirements.txt
```

### Railway 배포 실패
```bash
# 환경 변수 확인
# Flask는 port 8000에서 시작되어야 함
gunicorn --bind 0.0.0.0:8000 web.server:app
```

### iOS 빌드 실패
```bash
# 캐시 삭제 후 재시도
eas build --platform ios --clear-cache
```

### Android 빌드 실패
```bash
# Gradle 캐시 삭제
rm -rf android/.gradle
eas build --platform android --clear-cache
```

---

**체크리스트 상태**: 준비 완료 ✅  
**다음 액션**: Step 1-1부터 시작하세요!

