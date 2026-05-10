from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class PostContent:
    """업로드할 콘텐츠 데이터 구조"""
    title: str = ""
    body: str = ""
    hashtags: list[str] = field(default_factory=list)
    image_paths: list[str] = field(default_factory=list)
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    category: Optional[str] = None
    schedule_time: Optional[str] = None  # ISO 8601 형식

    @property
    def caption(self) -> str:
        hashtag_str = " ".join(self.hashtags) if self.hashtags else ""
        return f"{self.body}\n\n{hashtag_str}".strip()


@dataclass
class UploadResult:
    platform: str
    success: bool
    url: Optional[str] = None
    post_id: Optional[str] = None
    error: Optional[str] = None


class BasePlatform(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get("enabled", False)

    @abstractmethod
    def upload(self, content: PostContent) -> UploadResult:
        pass

    def validate_image(self, path: str, max_mb: float = 8.0) -> bool:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"이미지 파일 없음: {path}")
        size_mb = p.stat().st_size / (1024 * 1024)
        if size_mb > max_mb:
            raise ValueError(f"이미지 용량 초과: {size_mb:.1f}MB (최대 {max_mb}MB)")
        return True

    def validate_video(self, path: str, max_mb: float = 500.0) -> bool:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"영상 파일 없음: {path}")
        size_mb = p.stat().st_size / (1024 * 1024)
        if size_mb > max_mb:
            raise ValueError(f"영상 용량 초과: {size_mb:.1f}MB (최대 {max_mb}MB)")
        return True
