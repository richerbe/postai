import json
import time
from google import genai
from google.genai import types


class TrendAnalyzer:
    """Google 트렌드 + Gemini로 콘텐츠 주제 자동 기획"""

    def __init__(self, config: dict, business_info: dict = None):
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "gemini-2.5-flash")
        self.temperature = config.get("temperature", 0.8)
        self.client = genai.Client(api_key=self.api_key)
        self.business_info = business_info or {}

    def _ask(self, prompt: str) -> dict | list:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=self.temperature,
                response_mime_type="application/json",
            ),
        )
        text = response.text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("[") if text.find("[") < text.find("{") else text.find("{")
            if text.startswith("["):
                end = text.rfind("]") + 1
            else:
                end = text.rfind("}") + 1
            return json.loads(text[start:end])

    def fetch_korea_trends(self) -> list[str]:
        """Google 트렌드 한국 인기 검색어 가져오기"""
        try:
            from pytrends.request import TrendReq
            pt = TrendReq(hl="ko", tz=540, timeout=(10, 25))
            trending = pt.trending_searches(pn="south_korea")
            return trending[0].tolist()[:20]
        except Exception:
            # 네트워크 오류 시 기본 트렌드 반환
            return [
                "결혼반지", "커플링", "금값", "14k 금반지",
                "예물반지", "다이아몬드반지", "실버링", "금테크",
                "명품쥬얼리", "기념일선물"
            ]

    def analyze_trends_for_business(self, trends: list[str]) -> list[dict]:
        """트렌드를 비즈니스에 맞게 콘텐츠로 기획"""
        business_desc = self.business_info.get("description", "금반지, 커플링, 예물 판매 주얼리 쇼핑몰")
        account = self.business_info.get("account", "@geumseok_jewellery")

        prompt = f"""
당신은 SNS 콘텐츠 기획 전문가입니다.

비즈니스 정보:
- 계정: {account}
- 업종: {business_desc}

현재 한국 구글 인기 검색어 TOP 20:
{json.dumps(trends, ensure_ascii=False)}

위 트렌드를 분석해서, 이 비즈니스에 활용 가능한 콘텐츠 아이디어를 8개 추천해주세요.

각 아이디어는 다음 기준으로 선별하세요:
1. 트렌드와 비즈니스의 연관성이 높을 것
2. SNS에서 좋아요/공유가 많이 받을 수 있는 주제
3. 실제로 구매로 이어질 수 있는 주제

아래 JSON 배열로만 응답하세요:
[
  {{
    "topic": "포스트 주제 (구체적으로)",
    "angle": "콘텐츠 각도/관점 (예: 비교, 추천, 팁, 정보)",
    "reason": "이 주제를 선택한 이유 (트렌드 연결 설명, 1-2문장)",
    "trend_keyword": "연결된 트렌드 키워드",
    "platform": "최적 플랫폼 (instagram/youtube/blog)",
    "content_type": "콘텐츠 유형 (카드뉴스/릴스/일반포스트/블로그)",
    "hook": "첫 줄 후킹 문구 (눈길을 끄는 한 줄)",
    "score": 85
  }}
]

한국어로만 응답하세요.
"""
        result = self._ask(prompt)
        return sorted(result, key=lambda x: x.get("score", 0), reverse=True)

    def get_weekly_content_plan(self, num_days: int = 7) -> list[dict]:
        """일주일 콘텐츠 캘린더 자동 생성"""
        business_desc = self.business_info.get("description", "금반지, 커플링, 예물 판매 주얼리 쇼핑몰")

        prompt = f"""
당신은 SNS 콘텐츠 기획 전문가입니다.

비즈니스: {business_desc}
계정: {self.business_info.get("account", "@geumseok_jewellery")}

오늘부터 {num_days}일간의 SNS 콘텐츠 캘린더를 만들어주세요.

규칙:
- 월/수/금: Instagram 카드뉴스 (정보성)
- 화/목: Instagram 릴스 or Threads (일상/팁)
- 주말: YouTube 쇼츠 or 블로그 (심화 내용)
- 상품 홍보는 30%, 정보성 콘텐츠 70% 비율

아래 JSON 배열로만 응답하세요:
[
  {{
    "day": 1,
    "weekday": "월요일",
    "platform": "instagram",
    "content_type": "카드뉴스",
    "topic": "구체적인 포스트 주제",
    "hook": "후킹 문구",
    "hashtags": ["#해시태그1", "#해시태그2", "#해시태그3"]
  }}
]

한국어로만 응답하세요.
"""
        return self._ask(prompt)

    def get_trending_topics(self) -> list[dict]:
        """전체 프로세스: 트렌드 수집 → 분석 → 추천"""
        trends = self.fetch_korea_trends()
        ideas = self.analyze_trends_for_business(trends)
        return ideas, trends
