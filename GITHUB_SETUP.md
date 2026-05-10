# 🐙 GitHub에 코드 푸시하기

## Step 1: GitHub 저장소 생성

1. https://github.com/new 접속
2. 아래 정보로 저장소 생성:

**웹 프로젝트용**
```
Repository name: postai
Description: SNS 자동화 플랫폼 - AI 기반 멀티채널 콘텐츠 관리
Visibility: Public
```

**모바일 앱용** (별도)
```
Repository name: postai-mobile
Description: PostAI Mobile App - React Native + Expo
Visibility: Public
```

3. "Create repository" 클릭

---

## Step 2: 로컬에서 GitHub에 푸시

### 웹 프로젝트 푸시

```bash
cd /Users/macbook/Desktop/자동화

# GitHub 저장소 추가
git remote add origin https://github.com/YOUR_USERNAME/postai.git

# main 브랜치로 설정
git branch -M main

# GitHub에 푸시
git push -u origin main
```

**완료 확인**:
- https://github.com/YOUR_USERNAME/postai 접속
- 모든 파일이 보이는지 확인

### 모바일 프로젝트 푸시

```bash
cd /Users/macbook/Desktop/sns-mobile

# GitHub 저장소 추가
git remote add origin https://github.com/YOUR_USERNAME/postai-mobile.git

# main 브랜치로 설정
git branch -M main

# GitHub에 푸시
git push -u origin main
```

**완료 확인**:
- https://github.com/YOUR_USERNAME/postai-mobile 접속
- 모든 파일이 보이는지 확인

---

## Step 3: 배포 플랫폼 연동

### Streamlit Cloud 배포

1. https://streamlit.io/cloud 접속
2. "GitHub로 로그인" 선택
3. GitHub 계정으로 승인
4. "Create app" 클릭
5. 아래 정보 입력:
   - Repository: `YOUR_USERNAME/postai`
   - Branch: `main`
   - Main file path: `app.py`
6. "Deploy" 클릭
7. 배포 완료 대기 (2-3분)
8. ✅ URL: `https://YOUR_USERNAME-postai.streamlit.app`

### Railway 배포

1. https://railway.app 접속
2. GitHub 또는 이메일로 가입
3. "Create a new project" 클릭
4. "Deploy from GitHub repo" 선택
5. GitHub 권한 승인
6. `postai` 저장소 선택
7. 환경 변수 설정:

```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./postai.db
```

(SECRET_KEY 생성: `python -c "import secrets; print(secrets.token_hex(32))"`)

8. "Deploy" 클릭
9. 배포 완료 대기 (2-3분)
10. ✅ URL: https://postai.up.railway.app (또는 사용자 정의 도메인)

---

## 🎯 배포 후 테스트

### Streamlit 테스트
```
https://YOUR_USERNAME-postai.streamlit.app
로그인: admin / admin123
```

### Flask 웹사이트 테스트
```
https://postai.up.railway.app
모든 섹션이 로드되는지 확인
```

---

## ⚠️ 자주 묻는 질문

**Q: "fatal: not a git repository" 오류가 나요**
```bash
# 현재 디렉토리가 맞는지 확인
pwd
# /Users/macbook/Desktop/자동화 또는 /Users/macbook/Desktop/sns-mobile 이어야 함
```

**Q: "remote origin already exists" 오류가 나요**
```bash
# 기존 원격 제거
git remote remove origin
# 다시 추가
git remote add origin https://github.com/YOUR_USERNAME/postai.git
```

**Q: GitHub 로그인이 안 돼요**
- GitHub에서 Personal Access Token 생성: https://github.com/settings/tokens
- `git push` 시 비밀번호 대신 토큰 사용

**Q: "Permission denied (publickey)" 오류가 나요**
```bash
# SSH 키 설정 또는 HTTPS 사용
git remote set-url origin https://github.com/YOUR_USERNAME/postai.git
```

---

## 📊 다음 단계

배포 완료 후:

1. ✅ 웹사이트 접속 테스트
2. ✅ Streamlit 앱 기능 테스트
3. ✅ 모바일 배포 준비 ($124)
4. ✅ Apple Developer 계정 생성 ($99)
5. ✅ Google Play 계정 생성 ($25)
6. ✅ iOS 빌드 및 배포
7. ✅ Android 빌드 및 배포

---

**🚀 준비 완료! GitHub에 코드를 푸시하세요!**
