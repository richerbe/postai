import os
import pickle
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from .base import BasePlatform, PostContent, UploadResult

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "youtube_token.pickle"


class YouTubeUploader(BasePlatform):
    """YouTube Data API v3를 사용한 유튜브 업로드"""

    def __init__(self, config: dict):
        super().__init__(config)
        self.client_secrets = config.get("client_secrets_file", "youtube_client_secrets.json")
        self.default_category = config.get("default_category", "22")
        self.default_privacy = config.get("default_privacy", "public")
        self.default_language = config.get("default_language", "ko")
        self._service = None

    def _authenticate(self):
        creds = None
        token_path = Path(TOKEN_FILE)

        if token_path.exists():
            with open(token_path, "rb") as f:
                creds = pickle.load(f)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, "wb") as f:
                pickle.dump(creds, f)

        self._service = build("youtube", "v3", credentials=creds)

    def upload(self, content: PostContent) -> UploadResult:
        if not self.enabled:
            return UploadResult("youtube", False, error="YouTube 비활성화")
        if not content.video_path:
            return UploadResult("youtube", False, error="동영상 파일 경로 필요")

        try:
            self.validate_video(content.video_path)
            if not self._service:
                self._authenticate()

            body = {
                "snippet": {
                    "title": content.title or "제목 없음",
                    "description": content.caption,
                    "tags": content.tags or [],
                    "categoryId": content.category or self.default_category,
                    "defaultLanguage": self.default_language,
                },
                "status": {
                    "privacyStatus": self.default_privacy,
                    "selfDeclaredMadeForKids": False,
                },
            }

            media = MediaFileUpload(
                content.video_path,
                chunksize=-1,
                resumable=True,
                mimetype="video/*",
            )

            request = self._service.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media,
            )

            response = None
            while response is None:
                _, response = request.next_chunk()

            video_id = response["id"]

            # 썸네일 설정
            if content.thumbnail_path and Path(content.thumbnail_path).exists():
                self._service.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(content.thumbnail_path),
                ).execute()

            return UploadResult(
                "youtube", True,
                url=f"https://www.youtube.com/watch?v={video_id}",
                post_id=video_id,
            )
        except Exception as e:
            return UploadResult("youtube", False, error=str(e))
