# 🚀 Streamlit Cloud 배포 (무료)

## 단계 1: GitHub에 코드 푸시

```bash
cd /Users/macbook/Desktop/자동화

# GitHub 저장소 생성 (또는 기존 저장소 사용)
# https://github.com/new 에서 새 저장소 생성

# 저장소 연결
git remote add origin https://github.com/YOUR_USERNAME/postai.git
git branch -M main
git push -u origin main
```

## 단계 2: Streamlit Cloud에서 배포

1. **https://streamlit.io/cloud** 방문
2. **"Sign in with GitHub"** 클릭
3. **"Deploy an app"** → **"GitHub repository 선택"**
   - Repository: postai
   - Branch: main
   - Main file path: app.py
4. **"Deploy"** 클릭

## 단계 3: 배포 완료!

- URL: `https://YOUR-USERNAME-postai.streamlit.app`
- 자동으로 HTTPS 적용
- 무료 (월 1GB RAM, 1 vCPU)

## 환경변수 설정

1. Streamlit Cloud 대시보드 → 앱 선택
2. **Settings** → **Secrets**
3. `.env` 파일 내용 입력:

```
SECRET_KEY=your-secret-key
STRIPE_SECRET_KEY=sk_test_xxx
```

---

**완료!** ✅ Streamlit 앱이 클라우드에서 실행 중입니다!
