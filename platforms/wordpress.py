import requests
import base64
from pathlib import Path
from .base import BasePlatform, PostContent, UploadResult


class WordPressUploader(BasePlatform):
    """WordPress REST API를 사용한 업로드"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.url = config.get("url", "").rstrip("/")
        self.username = config.get("username", "")
        self.password = config.get("password", "")
        self.default_status = config.get("default_status", "publish")
        self.default_category_id = config.get("default_category_id", 1)

    @property
    def _auth_header(self) -> dict:
        token = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        return {"Authorization": f"Basic {token}"}

    def _upload_media(self, image_path: str) -> int:
        p = Path(image_path)
        suffix = p.suffix.lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}
        mime = mime_map.get(suffix, "image/jpeg")

        headers = {
            **self._auth_header,
            "Content-Disposition": f'attachment; filename="{p.name}"',
            "Content-Type": mime,
        }
        with open(image_path, "rb") as f:
            resp = requests.post(f"{self.url}/wp-json/wp/v2/media", headers=headers, data=f)
        resp.raise_for_status()
        return resp.json()["id"]

    def upload(self, content: PostContent) -> UploadResult:
        if not self.enabled:
            return UploadResult("wordpress", False, error="WordPress 비활성화")
        try:
            featured_media_id = None
            if content.image_paths:
                first_img = content.image_paths[0]
                if Path(first_img).exists():
                    featured_media_id = self._upload_media(first_img)

            # 추가 이미지를 본문 HTML에 삽입
            extra_images_html = ""
            for img_path in content.image_paths[1:]:
                if Path(img_path).exists():
                    media_id = self._upload_media(img_path)
                    resp = requests.get(
                        f"{self.url}/wp-json/wp/v2/media/{media_id}",
                        headers=self._auth_header,
                    )
                    img_url = resp.json().get("source_url", "")
                    extra_images_html += f'<img src="{img_url}" />\n'

            body_html = content.body.replace("\n", "<br>") + extra_images_html

            post_data = {
                "title": content.title or "제목 없음",
                "content": body_html,
                "status": self.default_status,
                "categories": [content.category or self.default_category_id],
                "tags": content.tags,
                "excerpt": content.body[:150] if content.body else "",
            }
            if featured_media_id:
                post_data["featured_media"] = featured_media_id

            resp = requests.post(
                f"{self.url}/wp-json/wp/v2/posts",
                json=post_data,
                headers=self._auth_header,
            )
            resp.raise_for_status()
            data = resp.json()

            return UploadResult(
                "wordpress", True,
                url=data.get("link", ""),
                post_id=str(data.get("id", "")),
            )
        except Exception as e:
            return UploadResult("wordpress", False, error=str(e))
