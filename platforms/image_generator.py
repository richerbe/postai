import time
import urllib.parse
import requests
from pathlib import Path


# Pollinations.ai - 완전 무료, 가입 불필요, Flux 모델 기반
POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"


class AIImageGenerator:
    """Pollinations.ai를 사용한 무료 이미지 생성 (가입/토큰 불필요)"""

    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)

    def _generate_one(self, prompt: str, save_path: str, width: int = 1024, height: int = 1024) -> str:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        encoded = urllib.parse.quote(prompt)
        url = f"{POLLINATIONS_URL.format(prompt=encoded)}?width={width}&height={height}&nologo=true&enhance=true"

        for attempt in range(3):
            try:
                resp = requests.get(url, timeout=60)
                if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
                    with open(save_path, "wb") as f:
                        f.write(resp.content)
                    return save_path
                time.sleep(5)
            except requests.exceptions.Timeout:
                time.sleep(5 * (attempt + 1))

        raise RuntimeError(f"이미지 생성 실패: {save_path}")

    def _kor_to_prompt(self, text: str, style: str = "general") -> str:
        """한국어 설명을 영어 프롬프트로 변환"""
        styles = {
            "cardnews": "clean infographic card news design, Korean social media style, minimal, professional, white background, bold typography, high quality",
            "thumbnail": "YouTube thumbnail, vibrant colors, high contrast, eye-catching, professional, bold text space, dramatic lighting",
            "general": "professional photo, high quality, detailed, sharp focus, modern design",
        }
        return f"{text}, {styles.get(style, styles['general'])}"

    def generate_image(self, prompt: str, num_images: int = 1, save_dir: str = "assets/images") -> list[str]:
        """프롬프트로 이미지 생성

        Args:
            prompt: 이미지 설명 (한글 가능)
            num_images: 생성 개수 (1-10)
            save_dir: 저장 경로
        """
        num_images = min(max(num_images, 1), 10)
        saved = []
        for i in range(num_images):
            path = f"{save_dir}/generated_{i + 1}.png"
            full_prompt = self._kor_to_prompt(prompt, "general")
            self._generate_one(full_prompt, path)
            saved.append(path)
            if i < num_images - 1:
                time.sleep(2)
        return saved

    def generate_cardnews(self, topic: str, num_cards: int = 3, save_dir: str = "assets/images") -> list[str]:
        """카드뉴스 시리즈 생성

        Args:
            topic: 주제 (예: "AI 마케팅")
            num_cards: 카드 개수 (1-5)
        """
        num_cards = min(max(num_cards, 1), 5)
        card_prompts = [
            f"{topic} introduction overview card 1",
            f"{topic} key points highlight infographic card 2",
            f"{topic} conclusion action items card 3",
            f"{topic} statistics data visualization card 4",
            f"{topic} final summary call to action card 5",
        ]
        saved = []
        for idx in range(num_cards):
            path = f"{save_dir}/cardnews_{idx + 1}.png"
            prompt = self._kor_to_prompt(card_prompts[idx], "cardnews")
            self._generate_one(prompt, path)
            saved.append(path)
            time.sleep(2)
        return saved

    def generate_thumbnail(self, video_title: str, save_dir: str = "assets/images") -> str:
        """YouTube 썸네일 생성 (16:9)"""
        prompt = self._kor_to_prompt(
            f"YouTube thumbnail for '{video_title}', bold text area, dramatic",
            "thumbnail",
        )
        path = f"{save_dir}/thumbnail_youtube.png"
        return self._generate_one(prompt, path, width=1024, height=576)

    def generate_variations(self, image_path: str, num_variations: int = 3, save_dir: str = "assets/images") -> list[str]:
        """이미지 변형 생성"""
        base_name = Path(image_path).stem
        saved = []
        for i in range(num_variations):
            path = f"{save_dir}/variation_{i + 1}.png"
            prompt = self._kor_to_prompt(f"{base_name} variation {i + 1}, similar style", "general")
            self._generate_one(prompt, path)
            saved.append(path)
            time.sleep(2)
        return saved
