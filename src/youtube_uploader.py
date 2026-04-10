import os
import time
import asyncio
from typing import Optional
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]
TOKEN_FILE = "youtube_token.pickle"
CLIENT_SECRET_FILE = os.getenv("YOUTUBE_CLIENT_SECRET", "client_secret.json")


class YouTubeUploader:
    """
    Handles authenticated YouTube video uploads.
    - Uses OAuth2 with token caching (youtube_token.pickle).
    - Defaults to Private (private) visibility for pre-approval workflow per rule.md.
    - Supports resumable uploads for large files.
    """

    def __init__(self):
        self.youtube = None

    def authenticate(self):
        """Authenticates and returns a YouTube API service object."""
        creds = None

        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CLIENT_SECRET_FILE):
                    raise FileNotFoundError(
                        f"YouTube OAuth2 client secret not found: {CLIENT_SECRET_FILE}\n"
                        "Please download it from Google Cloud Console and set YOUTUBE_CLIENT_SECRET in .env"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(TOKEN_FILE, "wb") as token:
                pickle.dump(creds, token)

        self.youtube = build("youtube", "v3", credentials=creds)
        return self.youtube

    def upload(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: Optional[list] = None,
        category_id: str = "24",          # "Entertainment"
        privacy_status: str = "private",  # per rule.md: default private
        thumbnail_path: Optional[str] = None,
    ) -> str:
        """
        Uploads a video to YouTube.
        Returns the video ID on success.
        """
        if self.youtube is None:
            self.authenticate()

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or ["판타지", "웹소설", "책읽어주는아저씨", "AutoBard"],
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            chunksize=10 * 1024 * 1024,     # 10MB chunks
            resumable=True,
        )

        request = self.youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media,
        )

        print(f"Starting YouTube upload: {os.path.basename(video_path)}")
        response = None
        retries = 0
        while response is None:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"  Upload progress: {pct}%")

        video_id = response.get("id", "")
        print(f"✅ YouTube upload complete. Video ID: {video_id}")
        print(f"   URL: https://www.youtube.com/watch?v={video_id}")

        # Optionally set thumbnail
        if thumbnail_path and os.path.exists(thumbnail_path):
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path),
            ).execute()
            print(f"   Thumbnail set: {thumbnail_path}")

        return video_id

    async def upload_async(self, video_path: str, **kwargs) -> str:
        """Async wrapper for use in the async pipeline."""
        return await asyncio.to_thread(self.upload, video_path, **kwargs)
