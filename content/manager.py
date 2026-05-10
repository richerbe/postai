import yaml
from pathlib import Path
from platforms.base import PostContent


class ContentManager:
    """YAML 파일에서 콘텐츠를 로드하고 관리"""

    @staticmethod
    def from_yaml(yaml_path: str) -> PostContent:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return PostContent(
            title=data.get("title", ""),
            body=data.get("body", ""),
            hashtags=data.get("hashtags", []),
            image_paths=data.get("image_paths", []),
            video_path=data.get("video_path"),
            thumbnail_path=data.get("thumbnail_path"),
            tags=data.get("tags", []),
            category=data.get("category"),
            schedule_time=data.get("schedule_time"),
        )

    @staticmethod
    def create_template(output_path: str = "posts/example_post.yaml"):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        template = {
            "title": "포스팅 제목",
            "body": "본문 내용을 여기에 작성하세요.\n여러 줄도 가능합니다.",
            "hashtags": ["#예시태그", "#자동화", "#SNS"],
            "image_paths": [
                "assets/images/card1.jpg",
                "assets/images/card2.jpg",
            ],
            "video_path": None,
            "thumbnail_path": None,
            "tags": ["예시", "자동화"],
            "category": None,
            "schedule_time": None,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(template, f, allow_unicode=True, default_flow_style=False)
        return output_path
