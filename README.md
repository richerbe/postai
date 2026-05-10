# 🚀 SNS 자동 업로드 시스템

다중 SNS 플랫폼을 한 번에 관리하고 콘텐츠를 자동으로 발행할 수 있는 통합 플랫폼입니다.

## ✨ 주요 기능 (28개 메뉴)

### 콘텐츠 제작
- 🔥 트렌드 기획 - AI 기반 트렌드 분석
- ✏️ 콘텐츠 기획실 - 전략 수립
- 🎯 AI 콘텐츠 기획 - 자동 아이디어 생성
- ✍️ 포스트 생성 - 텍스트 작성
- 🖼️ 이미지 생성 - AI 이미지
- 📹 숏폼 영상 - 15/30/60초 영상
- 🎴 카드뉴스 제작 - 멀티 페이지
- 📝 블로그 글 쓰기 - 자동 생성

### SNS 관리
- 🔗 계정 연동 - Instagram, YouTube, TikTok 등
- 📤 업로드 - 플랫폼별 발행
- ⏰ 예약 발행 - 시간대별 자동
- 📅 발행 캘린더 - 월간 계획
- 💬 DM 자동화 - 자동 응답

### 분석 & 리포팅
- 📊 성과 추적 - 실시간 모니터링
- 📄 리포트 생성 - PDF 리포트

### 팀 & 설정
- 👥 팀 멤버 관리 - 권한 관리
- 👥 사용자 관리 - 관리자 전용
- 🔌 API/MCP 연동 - 외부 서비스
- ⚙️ 설정 - 플랫폼 API 키

## 👥 다중 사용자 시스템

- **로그인**: 안전한 사용자 인증
- **권한 제어**:
  - 👁️ 뷰어: 보기만
  - ✏️ 편집자: 생성/편집/삭제
  - ⚙️ 관리자: 모든 기능 + 사용자 관리

## 🛠️ 기술 스택

- Backend: Flask, Streamlit (Python)
- Database: SQLite
- Payment: Stripe
- Deployment: Docker

---

## 📦 설치

### 로컬 개발

```bash
# 1. 저장소 클론
git clone <repo-url>
cd 자동화

# 2. 환경 변수 설정
cp .env.example .env
# .env 편집 후 API 키 입력

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 실행 (터미널 2개 열기)

# 터미널 1 - Flask
cd web && python -m flask run --port=8000

# 터미널 2 - Streamlit  
python -m streamlit run app.py --server.port=8501
```

**접속**: http://localhost:8000 (웹), http://localhost:8501 (앱)

**기본 계정**: admin / admin123

---

## 🐳 Docker 배포

### Docker Compose (권장)

```bash
chmod +x deploy.sh
./deploy.sh
# 또는
docker-compose up -d
```

### 클라우드 배포

#### Streamlit Cloud (무료)
1. GitHub 푸시
2. https://share.streamlit.io 방문
3. "New app" → app.py 선택

#### Heroku
```bash
heroku create your-app
heroku config:set SECRET_KEY=xxx STRIPE_SECRET_KEY=xxx
git push heroku main
```

#### AWS/GCP/Azure
Docker 이미지를 Container Services에 배포

---

## 🔐 환경변수 설정

필수:
```env
FLASK_ENV=production
SECRET_KEY=strong-random-string

# Stripe (필수)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_STARTER_PRICE_ID=price_...
STRIPE_PRO_PRICE_ID=price_...
```

선택:
```env
OPENAI_API_KEY=sk_...
GOOGLE_API_KEY=...
```

---

## ⚡ 프로덕션 체크리스트

- ✅ SECRET_KEY 변경
- ✅ 모든 API 키 설정
- ✅ HTTPS 활성화
- ✅ CORS 설정
- ✅ 데이터베이스 백업
- ✅ 로그 모니터링

---

## 📊 모니터링

```bash
# 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 헬스 체크
curl http://localhost:8000/
curl http://localhost:8501/
```

---

## 🆘 문제 해결

**포트 충돌**
```bash
lsof -i :8000
kill -9 <PID>
```

**데이터베이스 오류**
```bash
rm web/users.db
python -c "from web.server import init_db; init_db()"
```

**Streamlit 캐시**
```bash
rm -rf ~/.streamlit/
streamlit run app.py
```

---

## 📄 라이선스

MIT

---

**마지막 업데이트**: 2026-05-10
