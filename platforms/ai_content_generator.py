import json
import time
from google import genai
from google.genai import types
from platforms.base import PostContent

# 503 등 오류 발생 시 자동으로 fallback
FALLBACK_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]


class AIContentGenerator:
    """Google Gemini를 사용한 자동 포스트 생성 (완전 무료)"""

    def __init__(self, config: dict):
        self.enabled = config.get("enabled", False)
        self.api_key = config.get("api_key", "")
        self.model_name = config.get("model", "gemini-2.5-flash")
        self.temperature = config.get("temperature", 0.7)
        self.client = genai.Client(api_key=self.api_key)

    def _ask(self, prompt: str) -> dict:
        models_to_try = [self.model_name] + [m for m in FALLBACK_MODELS if m != self.model_name]
        last_error = None

        for model in models_to_try:
            for attempt in range(3):
                try:
                    response = self.client.models.generate_content(
                        model=model,
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
                        start = text.find("{")
                        end = text.rfind("}") + 1
                        if start >= 0 and end > start:
                            return json.loads(text[start:end])
                        raise ValueError(f"응답 파싱 실패: {text[:200]}")
                except Exception as e:
                    last_error = e
                    err_str = str(e)
                    if "503" in err_str or "UNAVAILABLE" in err_str:
                        time.sleep(5 * (attempt + 1))
                        continue
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        # 권장 대기시간 파싱 (없으면 10초 대기)
                        import re
                        delay_match = re.search(r"retryDelay.*?(\d+)s", err_str)
                        wait = int(delay_match.group(1)) + 2 if delay_match else 10
                        time.sleep(wait)
                        continue
                    break  # 다른 오류는 다음 모델로
            else:
                continue  # 3회 재시도 모두 실패 → 다음 모델

        raise RuntimeError(f"모든 모델 시도 실패: {last_error}")

    def _parse(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            raise ValueError(f"Gemini 응답 파싱 실패: {text[:200]}")

    PLATFORM_STYLES = {
        "instagram": "Instagram 카드뉴스/릴스 스타일 (140-200자, 캐주얼, 이모지 포함, 공감 유도)",
        "youtube":   "YouTube 영상 설명 스타일 (200-400자, 정보성, 마지막에 구독 CTA 포함)",
        "blog":      "블로그 포스트 스타일 (500-800자, 소제목 포함, 친절한 설명체)",
        "threads":   "Threads 스타일 (80-120자, 간결, 솔직한 대화체)",
        "all":       "모든 플랫폼 공용 (200-250자, 균형잡힌 정보형)",
    }

    def generate_post(
        self,
        topic: str,
        platform: str = "all",
        include_hashtags: bool = True,
        num_hashtags: int = 5,
    ) -> PostContent:
        style = self.PLATFORM_STYLES.get(platform, self.PLATFORM_STYLES["all"])
        prompt = f"""
주제: {topic}
플랫폼 스타일: {style}
해시태그: {"한글 " + str(num_hashtags) + "개 포함" if include_hashtags else "제외"}

아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{
    "title": "제목 (10-20자)",
    "body": "본문 내용",
    "tags": ["태그1", "태그2", "태그3"],
    "hashtags": ["#해시태그1", "#해시태그2"]
}}

한국어로만 작성하세요.
"""
        data = self._ask(prompt)
        return PostContent(
            title=data.get("title", ""),
            body=data.get("body", ""),
            tags=data.get("tags", []),
            hashtags=data.get("hashtags", []),
        )

    def optimize_for_platform(self, content: PostContent, platform: str) -> PostContent:
        requirements = {
            "instagram": "최대 150자, 캐주얼톤, 이모지 포함",
            "youtube":   "200-400자, 정보성, 구독/좋아요 CTA 포함",
            "blog":      "500-800자, 소제목 포함, 상세 설명",
            "threads":   "최대 100자, 간결, 솔직한 대화체",
        }
        prompt = f"""
원본 제목: {content.title}
원본 본문: {content.body}

"{platform}" 플랫폼 최적화 요구사항: {requirements.get(platform, "적절히 최적화")}

아래 JSON 형식으로만 응답하세요:
{{
    "title": "최적화된 제목",
    "body": "최적화된 본문",
    "hashtags": ["#해시태그1", "#해시태그2", "#해시태그3"]
}}

한국어로만 작성하세요.
"""
        data = self._ask(prompt)
        return PostContent(
            title=data.get("title", content.title),
            body=data.get("body", content.body),
            tags=content.tags,
            hashtags=data.get("hashtags", content.hashtags),
            image_paths=content.image_paths,
            video_path=content.video_path,
        )

    def batch_generate(self, topic: str, platforms: list[str] = None) -> dict[str, PostContent]:
        if platforms is None:
            platforms = ["instagram", "threads", "youtube", "blog"]

        base = self.generate_post(topic, platform="all")
        results = {}
        for plat in platforms:
            results[plat] = self.optimize_for_platform(base, plat)
            time.sleep(4)  # 분당 15회 제한 준수
        return results
