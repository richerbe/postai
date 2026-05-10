import re
import json
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from google import genai
from google.genai import types


def extract_video_id(url: str) -> str:
    """유튜브 URL에서 영상 ID 추출"""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
        r"(?:shorts\/)([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"유효하지 않은 유튜브 URL: {url}")


def get_video_info(video_id: str) -> dict:
    """영상 제목·채널 정보 가져오기 (oEmbed API 사용 - 무료)"""
    try:
        resp = requests.get(
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json",
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "title": data.get("title", ""),
                "author": data.get("author_name", ""),
                "thumbnail": data.get("thumbnail_url", ""),
            }
    except Exception:
        pass
    return {"title": "", "author": "", "thumbnail": ""}


def get_transcript(video_id: str) -> str:
    """자막 추출 (수동 자막 → 자동생성 자막 → yt-dlp 순서로 시도)"""
    url = f"https://www.youtube.com/watch?v={video_id}"

    # 1. youtube-transcript-api: 수동 + 자동생성 모두 시도
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        # 한국어 우선
        for lang in ["ko", "en"]:
            try:
                t = transcript_list.find_transcript([lang])
                fetched = t.fetch()
                return " ".join([item["text"] for item in fetched])
            except Exception:
                pass
        # 자동생성 자막
        for t in transcript_list:
            try:
                fetched = t.fetch()
                text = " ".join([item["text"] for item in fetched])
                if len(text) > 100:
                    return text
            except Exception:
                pass
    except (TranscriptsDisabled, Exception):
        pass

    # 2. yt-dlp로 자동생성 자막 추출
    try:
        import yt_dlp
        ydl_opts = {
            "skip_download": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["ko", "en"],
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # 자동생성 자막에서 텍스트 추출
            auto_subs = info.get("automatic_captions", {})
            for lang in ["ko", "en"]:
                if lang in auto_subs:
                    for fmt in auto_subs[lang]:
                        if fmt.get("ext") == "json3":
                            sub_url = fmt["url"]
                            resp = requests.get(sub_url, timeout=15)
                            if resp.ok:
                                data = resp.json()
                                texts = []
                                for event in data.get("events", []):
                                    for seg in event.get("segs", []):
                                        t = seg.get("utf8", "").strip()
                                        if t and t != "\n":
                                            texts.append(t)
                                result = " ".join(texts)
                                if len(result) > 100:
                                    return result
    except Exception:
        pass

    raise RuntimeError(
        "이 영상은 자막/자동자막이 없어 분석할 수 없습니다.\n"
        "자막이 있는 다른 영상을 사용해주세요."
    )


class YouTubeContentAnalyzer:
    """유튜브 영상 분석 → 우리 스타일 콘텐츠 재생성"""

    def __init__(self, config: dict, business_info: dict = None):
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "gemini-2.5-flash")
        self.client = genai.Client(api_key=self.api_key)
        self.business_info = business_info or {}

    def _ask(self, prompt: str) -> dict | list:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                response_mime_type="application/json",
            ),
        )
        text = response.text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = min(
                text.find("{") if text.find("{") >= 0 else 9999,
                text.find("[") if text.find("[") >= 0 else 9999,
            )
            if text.startswith("["):
                return json.loads(text[start:text.rfind("]") + 1])
            return json.loads(text[start:text.rfind("}") + 1])

    def analyze(self, url: str) -> dict:
        """URL 하나로 전체 분석 실행"""
        video_id = extract_video_id(url)
        info = get_video_info(video_id)
        script = get_transcript(video_id)

        # 스크립트가 너무 길면 앞부분만 사용 (Gemini 토큰 제한 고려)
        script_preview = script[:6000] if len(script) > 6000 else script

        business_desc = self.business_info.get("description", "주얼리 쇼핑몰")
        account = self.business_info.get("account", "@geumseok_jewellery")
        brand_voice = self.business_info.get(
            "brand_voice",
            "친근하고 전문적인 톤. 금·주얼리 전문가처럼 쉽게 설명. 구매자 입장에서 공감. 이모지 적절히 사용.",
        )

        prompt = f"""
당신은 SNS 콘텐츠 전문가입니다.

아래 유튜브 영상 스크립트를 분석하고, 우리 브랜드 스타일로 완전히 새로운 콘텐츠를 만들어주세요.

=== 원본 영상 정보 ===
제목: {info.get('title', '알 수 없음')}
채널: {info.get('author', '알 수 없음')}

=== 원본 스크립트 (일부) ===
{script_preview}

=== 우리 브랜드 정보 ===
계정: {account}
업종: {business_desc}
말투/톤: {brand_voice}

=== 요청 사항 ===
1. 원본 영상의 핵심 인사이트와 유용한 정보를 추출
2. 우리 브랜드(주얼리)에 맞게 각색
3. 표절이 되지 않도록 완전히 새로운 표현으로 재작성
4. 각 플랫폼별 최적 버전 생성

아래 JSON 형식으로만 응답하세요:
{{
  "video_summary": "원본 영상 핵심 내용 요약 (3-5문장)",
  "key_insights": ["핵심 인사이트1", "핵심 인사이트2", "핵심 인사이트3"],
  "instagram_post": {{
    "title": "인스타 포스트 제목",
    "body": "인스타 본문 (150-200자, 이모지 포함, 우리 브랜드 말투)",
    "hashtags": ["#해시태그1", "#해시태그2", "#해시태그3", "#해시태그4", "#해시태그5"]
  }},
  "threads_post": {{
    "title": "쓰레드 제목",
    "body": "쓰레드 본문 (100자 이내, 대화체)",
    "hashtags": ["#해시태그1", "#해시태그2"]
  }},
  "youtube_script": {{
    "title": "유튜브 영상 제목 (우리 채널 버전)",
    "hook": "첫 10초 후킹 멘트",
    "script": "유튜브 영상 스크립트 (500-800자)",
    "description": "영상 설명란 (200자)",
    "hashtags": ["#해시태그1", "#해시태그2", "#해시태그3"]
  }},
  "blog_post": {{
    "title": "블로그 포스트 제목",
    "body": "블로그 본문 (800-1200자, 소제목 포함, 구체적인 정보 위주)",
    "tags": ["태그1", "태그2", "태그3"]
  }},
  "cardnews_idea": {{
    "title": "카드뉴스 제목",
    "cards": [
      {{"card_num": 1, "heading": "카드1 제목", "content": "카드1 내용 (30자 이내)"}},
      {{"card_num": 2, "heading": "카드2 제목", "content": "카드2 내용 (30자 이내)"}},
      {{"card_num": 3, "heading": "카드3 제목", "content": "카드3 내용 (30자 이내)"}}
    ]
  }}
}}

한국어로만 응답하세요.
"""
        result = self._ask(prompt)
        result["video_info"] = info
        result["video_id"] = video_id
        result["original_url"] = url
        return result
