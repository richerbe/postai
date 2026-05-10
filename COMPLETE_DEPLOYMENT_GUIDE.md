# 🚀 완전 배포 가이드 (웹 + 모바일)

PostAI 전체 시스템을 프로덕션에 배포하는 단계별 가이드입니다.

---

## 📊 배포 구조

```
🌍 웹 버전
├── 🤖 Streamlit 앱 → Streamlit Cloud (무료)
│   └── URL: https://YOUR-USERNAME-postai.streamlit.app
│
├── 📱 Flask 웹사이트 → Railway (무료 크레딧)
│   └── URL: https://postai.up.railway.app
│
└── 💾 데이터베이스 → SQLite (내부)

📱 모바일 버전
├── 🍎 iOS 앱 → App Store (1-3일 심사)
│   └── 비용: $99/년 (Apple Developer)
│
└── 🤖 Android 앱 → Play Store (1-3시간 심사)
    └── 비용: $25 (일회, Google Play)
```

---

## 📋 전체 비용

| 항목 | 비용 | 기간 |
|-----|------|------|
| Streamlit Cloud | **무료** | 무제한 |
| Railway | **무료** ($5/월 크레딧) | 매월 |
| Expo | **무료** | 무제한 |
| Apple Developer | $99 | 매년 |
| Google Play | $25 | 일회 |
| **합계** | **$124** | 초기 + 연간 $99 |

---

## 🔄 배포 순서

### Phase 1: 준비 (지금)
1. GitHub에 코드 푸시
2. 계정 생성 (Expo, Apple, Google)

### Phase 2: 웹 배포 (30분)
1. Streamlit Cloud 배포
2. Railway 배포

### Phase 3: 모바일 배포 (1-3일)
1. Expo 빌드
2. App Store 제출
3. Play Store 제출
4. 심사 대기

---

## 🌐 PHASE 1: 웹 배포

### 단계 1: GitHub 준비

```bash
cd /Users/macbook/Desktop/자동화

# 1. GitHub 저장소 생성
# https://github.com/new 방문
# Repository name: postai

# 2. 저장소 연결
git remote add origin https://github.com/YOUR_USERNAME/postai.git
git branch -M main
git push -u origin main
```

### 단계 2: Streamlit Cloud 배포 (무료)

```
1. https://streamlit.io/cloud 방문
2. "Sign in with GitHub" 클릭
3. 저장소 선택 (postai)
4. Main file: app.py
5. "Deploy" 클릭

✅ 완료! URL: https://YOUR-USERNAME-postai.streamlit.app
```

### 단계 3: Railway 배포 (무료)

```
1. https://railway.app 방문
2. GitHub로 로그인
3. "New Project" → "Deploy from GitHub"
4. 저장소 선택 (postai)
5. 환경변수 추가:
   FLASK_ENV=production
   SECRET_KEY=your-secret-key
6. "Deploy" 클릭

✅ 완료! URL: https://postai.up.railway.app
```

---

## 📱 PHASE 2: 모바일 배포

### 준비: 계정 생성 (비용 필요)

#### 1️⃣ Apple Developer 계정 ($99/년)
```
1. https://developer.apple.com 방문
2. "Account" → 가입
3. 신용카드 등록
4. $99 결제
5. 개발팀 ID 저장
```

#### 2️⃣ Google Play 계정 ($25 일회)
```
1. https://play.google.com/console 방문
2. 가입 → $25 결제
3. 개발자 계정 생성
4. API 활성화
```

#### 3️⃣ Expo 계정 (무료)
```bash
npm install -g eas-cli
eas login  # 계정 생성 및 로그인
```

### 단계 1: iOS 앱 배포

```bash
cd /Users/macbook/Desktop/sns-mobile

# 1. Expo 설정
eas build:configure

# 2. iOS 빌드 (약 20분)
eas build --platform ios

# 3. App Store 제출
eas submit --platform ios

# 4. App Store Connect에서:
#    - 앱 정보 입력
#    - 스크린샷 4개 업로드
#    - 개인정보정책 입력
#    - "Submit for Review" 클릭

# 5. Apple 심사 (1-3일)
# 6. 승인 후 자동 배포
```

### 단계 2: Android 앱 배포

```bash
cd /Users/macbook/Desktop/sns-mobile

# 1. Android 빌드 (약 15분)
eas build --platform android

# 2. Play Store 제출
eas submit --platform android

# 3. Google Play Console에서:
#    - 앱 정보 입력
#    - 스크린샷 4개 업로드
#    - 개인정보정책 입력
#    - "Submit for review" 클릭

# 4. Google 심사 (1-3시간)
# 5. 승인 후 자동 배포
```

---

## 🎯 최종 체크리스트

### ✅ Phase 1: 웹 배포
- [ ] GitHub에 코드 푸시
- [ ] Streamlit Cloud 배포 완료
  - URL: `https://YOUR-USERNAME-postai.streamlit.app`
- [ ] Railway 배포 완료
  - URL: `https://postai.up.railway.app`

### ✅ Phase 2: 모바일 배포
- [ ] Expo 계정 생성
- [ ] Apple Developer 계정 ($99)
- [ ] Google Play 계정 ($25)
- [ ] iOS 빌드 및 제출
- [ ] Android 빌드 및 제출
- [ ] App Store 심사 완료 (1-3일)
- [ ] Play Store 심사 완료 (1-3시간)

---

## 🔍 배포 후 확인

### 웹 버전 확인

```bash
# Streamlit 앱
curl https://YOUR-USERNAME-postai.streamlit.app

# Flask 웹사이트
curl https://postai.up.railway.app
```

### 모바일 버전 확인

1. **iOS**: App Store에서 "PostAI" 검색
2. **Android**: Play Store에서 "PostAI" 검색
3. 설치 및 로그인 테스트

---

## 📈 배포 후 모니터링

### Streamlit Cloud
- 대시보드에서 로그 확인
- 사용자 피드백 모니터링

### Railway
- 대시보드에서 로그 확인
- CPU/메모리 사용량 모니터링
- 무료 크레딧 초과 시 알림 받기

### App Store / Play Store
- 리뷰 및 평점 모니터링
- 크래시 보고서 확인
- 사용자 피드백 수집

---

## 🆘 배포 문제 해결

### Streamlit 배포 실패
```bash
# requirements.txt 확인
cat requirements.txt

# 문법 확인
python -m py_compile app.py

# 재배포
git push origin main
```

### Railway 배포 실패
```bash
# 로그 확인
railway logs

# 환경변수 확인
railway variables

# 재배포
railway up
```

### iOS 빌드 실패
```bash
# 캐시 삭제
eas build --platform ios --clear-cache

# 재빌드
eas build --platform ios
```

### Android 빌드 실패
```bash
# 캐시 삭제
eas build --platform android --clear-cache

# 재빌드
eas build --platform android
```

---

## 📞 지원

| 서비스 | 문서 | 지원 |
|--------|------|------|
| Streamlit Cloud | https://docs.streamlit.io | docs@streamlit.io |
| Railway | https://docs.railway.app | support@railway.app |
| Expo | https://docs.expo.dev | forums.expo.dev |
| Apple | https://developer.apple.com | developer.apple.com/support |
| Google | https://play.google.com/console/support | google.com/support |

---

## 🎉 완료!

축하합니다! PostAI를 모든 플랫폼에 배포했습니다!

- 🌍 웹사이트: `https://postai.up.railway.app`
- 🤖 Streamlit: `https://YOUR-USERNAME-postai.streamlit.app`
- 🍎 iOS: App Store
- 🤖 Android: Play Store

**다음 단계**:
1. 사용자 피드백 수집
2. 버그 수정 및 기능 개선
3. 정기적인 업데이트 (월 1-2회)

---

**마지막 업데이트**: 2026-05-10
