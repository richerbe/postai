# 🚀 소셜미디어 멀티플랫폼 자동 업로드 시스템

**Instagram · Threads · YouTube · 네이버 블로그 · WordPress**에 콘텐츠를 자동 업로드합니다.  
**ChatGPT + DALL-E**로 텍스트와 이미지를 AI 자동 생성까지 가능합니다!

---

## ✨ 핵심 기능

| 기능 | 설명 |
|------|------|
| 🤖 **AI 포스트 생성** | ChatGPT로 제목, 본문, 해시태그 자동 작성 |
| 🎨 **AI 이미지 생성** | DALL-E로 카드뉴스, 썸네일 자동 제작 |
| 📤 **멀티 플랫폼 발행** | 5개 플랫폼에 동시 발행 |
| ⏰ **예약 발행** | 특정 시간 또는 정기 발행 |
| 🔄 **플랫폼별 최적화** | 각 SNS에 맞춰 텍스트 자동 변환 |
| 📹 **카드뉴스 시리즈** | 다중 페이지 카드뉴스 자동 생성 |

---

## 🎯 사용 시나리오

### 시나리오 1️⃣: "AI 마케팅" 주제로 전체 자동화 (5분)
```bash
# 포스트 + 이미지 + 발행 모두 자동!
python main.py generate-complete "AI 마케팅 트렌드" --cards 3 -p instagram -p threads -p youtube
```

결과:
- ✅ ChatGPT가 Instagram, Threads, YouTube용 포스트 생성
- ✅ DALL-E가 카드뉴스 3장 생성
- ✅ 자동으로 플랫폼에 발행 (이미지 포함)

### 시나리오 2️⃣: 수동으로 단계별 진행
```bash
# 1. 포스트만 생성
python main.py generate "소셜미디어 마케팅" --save posts/social.yaml

# 2. 카드뉴스 이미지 생성
python main.py generate-cardnews "소셜미디어 마케팅" --cards 3

# 3. 업로드
python main.py upload posts/social.yaml -p instagram -p threads
```

### 시나리오 3️⃣: 유튜브 영상 + 썸네일 자동 생성
```bash
python main.py generate-thumbnail "ChatGPT로 마케팅 자동화하기"
# → assets/images/thumbnail_youtube.png 생성됨

# posts/youtube_post.yaml에 썸네일 경로 추가 후
python main.py upload posts/youtube_post.yaml -p youtube
```

---

## 🚀 빠른 시작

### 1단계: 설치
```bash
chmod +x setup.sh && ./setup.sh
source venv/bin/activate
```

### 2단계: API 키 설정

#### OpenAI (ChatGPT + DALL-E)
1. https://platform.openai.com/account/api-keys 접속
2. **Create new secret key** → 복사
3. `config.yaml` 수정:
```yaml
openai:
  enabled: true
  api_key: "sk-proj-xxxxxxxxxxxxx"  # ← 붙여넣기
  model: "gpt-4o"  # 또는 gpt-3.5-turbo (저렴)
```

#### 인스타그램/Threads/YouTube/WordPress
[원래 설명서 참고](#api-설정-가이드)

### 3단계: 포스트 생성 및 발행
```bash
# 한 줄로 완성!
python main.py generate-complete "내 주제" --cards 3 -p instagram -p threads
```

---

## 📋 전체 명령어 목록

### 📝 포스트 생성
| 명령어 | 설명 |
|--------|------|
| `generate` | 단일 플랫폼용 포스트 생성 |
| `generate-batch` | 여러 플랫폼용 포스트 한 번에 생성 |
| `generate-complete` | 포스트 + 이미지 + 발행 모두 자동 |

### 🎨 이미지 생성
| 명령어 | 설명 |
|--------|------|
| `generate-image` | 일반 이미지 생성 |
| `generate-cardnews` | 카드뉴스 시리즈 생성 |
| `generate-thumbnail` | YouTube 썸네일 생성 |

### 📤 업로드
| 명령어 | 설명 |
|--------|------|
| `upload` | 즉시 업로드 |
| `schedule` | 특정 시간에 예약 업로드 |
| `schedule-recurring` | 매일/매주 반복 예약 |

### ⚙️ 관리
| 명령어 | 설명 |
|--------|------|
| `new-post` | YAML 템플릿 생성 |
| `check-config` | API 설정 상태 확인 |

---

## 💡 명령어 예시

### 💬 텍스트만 생성
```bash
# 인스타용 포스트 생성 (저장)
python main.py generate "AI 자동화 기초" -p instagram --save posts/ai_intro.yaml

# 여러 플랫폼용 동시 생성
python main.py generate-batch "마케팅 팁" -p instagram -p youtube -p blog
```

### 🖼️ 이미지만 생성
```bash
# 일반 이미지 3장
python main.py generate-image "한국식 미니멀 디자인" -n 3

# 카드뉴스 시리즈 (4장)
python main.py generate-cardnews "SNS 마케팅 전략" --cards 4

# YouTube 썸네일
python main.py generate-thumbnail "ChatGPT 활용법"
```

### 📤 업로드
```bash
# 즉시 업로드
python main.py upload posts/my_post.yaml -p instagram -p threads

# 특정 시간에 업로드 (2024-12-25 오전 9시)
python main.py schedule posts/my_post.yaml 2024-12-25T09:00:00 -p instagram

# 매일 오전 9시에 반복 업로드
python main.py schedule-recurring posts/daily.yaml "0 9 * * *" -p instagram -p youtube

# 평일만 오전 9시 (월~금)
python main.py schedule-recurring posts/weekday.yaml "0 9 * * 1-5" -p threads
```

### 🎯 완전 자동화 (최고 추천!)
```bash
# 1줄로 전부 해결: 포스트 생성 + 이미지 생성 + 발행
python main.py generate-complete "인공지능의 미래" --cards 3 -p instagram -p threads -p youtube

# 결과:
# ✓ ChatGPT: Instagram, Threads, YouTube용 포스트 생성
# ✓ DALL-E: 3장 카드뉴스 생성
# ✓ 자동 발행: 모든 포스트 + 이미지 동시 업로드
```

---

## 🛠️ 설정 파일 (`config.yaml`)

```yaml
openai:
  enabled: true
  api_key: "sk-proj-xxxxx"
  model: "gpt-4o"              # gpt-4o / gpt-3.5-turbo
  temperature: 0.7              # 창의성 (0.0~1.0)
  image_quality: "standard"     # standard / hd
  image_size: "1024x1024"       # 이미지 크기

instagram:
  enabled: true
  username: "YOUR_USERNAME"
  password: "YOUR_PASSWORD"
  # API 방식 또는 ID/PW 자동화 중 선택

threads:
  enabled: true
  username: "YOUR_USERNAME"
  password: "YOUR_PASSWORD"

youtube:
  enabled: true
  client_secrets_file: "youtube_client_secrets.json"

naver_blog:
  enabled: true
  naver_id: "YOUR_ID"
  naver_password: "YOUR_PASSWORD"
  blog_id: "YOUR_BLOG_ID"

wordpress:
  enabled: true
  url: "https://your-site.com"
  username: "YOUR_USERNAME"
  password: "YOUR_APP_PASSWORD"
```

---

## 📊 플랫폼별 특징

| 플랫폼 | 인증 | 카드뉴스 | 영상 | 예약 | 비용 |
|--------|------|---------|------|------|------|
| Instagram | ID/PW | ✅ 캐러셀 | ✅ | ✅ | 무료 |
| Threads | ID/PW | ✅ 캐러셀 | - | - | 무료 |
| YouTube | OAuth | - | ✅ | ✅ | 무료 |
| 네이버 블로그 | ID/PW | ✅ | ✅ | - | 무료 |
| WordPress | 자체 | ✅ | ✅ | ✅ | 자체 호스팅 |

---

## 🔧 트러블슈팅

### API 키 에러
```
"오류: OpenAI가 비활성화되어 있습니다"

→ config.yaml에서 openai.enabled: true 확인
→ api_key 입력 확인
```

### 인스타그램/Threads 로그인 실패
```
"Selenium 로그인 실패"

→ username/password 다시 확인
→ 2단계 인증 비활성화 후 재시도
→ 비정상 접속 차단된 경우 앱 비밀번호 사용
```

### 이미지 생성 타임아웃
```
"DALL-E 이미지 생성 실패"

→ 네트워크 확인
→ API 쿼터 확인 (platform.openai.com/account/api-limits)
→ 프롬프트 단순화
```

---

## 📈 성능 팁

1. **배치 생성이 더 빠름**
   ```bash
   # 느림: 플랫폼별로 각각 생성
   python main.py generate "주제" -p instagram
   python main.py generate "주제" -p threads
   
   # 빠름: 한 번에 생성
   python main.py generate-batch "주제" -p instagram -p threads
   ```

2. **가격 최적화**
   - `gpt-4o` (비쌈, 추천) vs `gpt-3.5-turbo` (더 저렴)
   - DALL-E `standard` (빠름) vs `hd` (고품질)

3. **인스타그램 카드뉴스**
   - 최대 10장까지 가능 (권장 3~5장)
   - 정사각형 이미지 권장

---

## 🎓 학습 자료

- [ChatGPT API 가이드](https://platform.openai.com/docs/guides/gpt)
- [DALL-E 이미지 생성](https://platform.openai.com/docs/guides/images)
- [Meta Graph API](https://developers.facebook.com/docs/instagram-api)
- [YouTube 데이터 API](https://developers.google.com/youtube/v3)

---

## 📞 피드백 & 이슈

문제가 있으신가요?
1. `python main.py check-config`로 설정 확인
2. 각 플랫폼의 API 상태 확인
3. 네트워크 연결 확인

---

**마지막 업데이트**: 2026-05-11  
**버전**: 2.0 (AI 자동 생성 지원)
