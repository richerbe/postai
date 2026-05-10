# 🚀 Railway에 웹 배포 (무료 크레딧)

## 단계 1: Railway 가입

1. **https://railway.app** 방문
2. **"Start Project"** → **"GitHub로 로그인"**
3. GitHub 인증 완료

## 단계 2: 프로젝트 생성

1. **"New Project"** 클릭
2. **"Deploy from GitHub repo"** 선택
3. **GitHub 저장소 선택** (postai)
4. **"Deploy Now"** 클릭

## 단계 3: 환경변수 설정

1. Railway 대시보드 → Variables
2. 다음 값 추가:

```
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-12345
FLASK_APP=web/server.py
```

## 단계 4: 도메인 연결 (선택)

1. **Settings** → **Domain**
2. **Generate Domain** 또는 **Connect Custom Domain**
3. URL: `https://postai.up.railway.app` (자동 생성)

## 단계 5: 배포 완료!

- Flask 웹사이트가 자동 배포됨
- URL: `https://postai.up.railway.app` (또는 커스텀 도메인)
- 무료 크레딧 $5/월
- 초과 시 유료 (약 $5-10/월)

---

✅ 웹사이트가 클라우드에서 실행 중입니다!
