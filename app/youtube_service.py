from __future__ import annotations

from datetime import datetime, timezone

import requests

from .models import ChannelModel, VideoModel

BASE = "https://www.googleapis.com/youtube/v3"


class YouTubeService:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key.strip()
        self._session = requests.Session()

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    def get_channel(self, user_input: str) -> ChannelModel | None:
        if not self.is_configured:
            raise RuntimeError("Chua cau hinh YouTube Data API v3 key.")

        channel_id = self._extract_channel_id(user_input)

        if channel_id:
            params = {"part": "snippet,statistics", "id": channel_id, "key": self._api_key}
        else:
            handle = self._extract_handle(user_input)
            if not handle:
                return None
            params = {"part": "snippet,statistics", "forHandle": handle, "key": self._api_key}

        resp = self._session.get(f"{BASE}/channels", params=params, timeout=30)
        self._raise_for_api_error(resp)
        items = resp.json().get("items", [])
        if not items:
            return None

        item = items[0]
        sn = item["snippet"]
        st = item.get("statistics", {})
        return ChannelModel(
            channel_id=item["id"],
            title=sn.get("title", user_input),
            url=user_input,
            subscribers=int(st.get("subscriberCount", 0)),
            video_count=int(st.get("videoCount", 0)),
            view_count=int(st.get("viewCount", 0)),
            published_at=self._parse_iso(sn.get("publishedAt")),
            last_checked=datetime.now(timezone.utc),
        )

    def get_latest_videos(self, channel_id: str, db_id: int, take: int = 3) -> list[VideoModel]:
        if not self.is_configured:
            raise RuntimeError("Chua cau hinh YouTube Data API v3 key.")

        resp = self._session.get(
            f"{BASE}/channels",
            params={"part": "contentDetails", "id": channel_id, "key": self._api_key},
            timeout=30,
        )
        self._raise_for_api_error(resp)
        items = resp.json().get("items", [])
        if not items:
            return []
        uploads = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

        resp = self._session.get(
            f"{BASE}/playlistItems",
            params={"part": "contentDetails", "playlistId": uploads,
                    "maxResults": take, "key": self._api_key},
            timeout=30,
        )
        self._raise_for_api_error(resp)
        video_ids = [
            it["contentDetails"]["videoId"]
            for it in resp.json().get("items", [])
        ]
        if not video_ids:
            return []

        resp = self._session.get(
            f"{BASE}/videos",
            params={"part": "snippet,statistics", "id": ",".join(video_ids),
                    "key": self._api_key},
            timeout=30,
        )
        self._raise_for_api_error(resp)

        videos = []
        for item in resp.json().get("items", []):
            sn = item["snippet"]
            st = item.get("statistics", {})
            videos.append(VideoModel(
                video_id=item["id"],
                channel_db_id=db_id,
                title=sn.get("title", ""),
                published_at=self._parse_iso(sn.get("publishedAt")),
                views=int(st.get("viewCount", 0)),
                likes=int(st.get("likeCount", 0)),
                comments=int(st.get("commentCount", 0)),
            ))
        videos.sort(key=lambda v: v.published_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return videos

    @staticmethod
    def _extract_handle(text: str) -> str | None:
        text = text.strip()
        if text.startswith("@"):
            return text[1:].split("?")[0].strip("/")
        if "youtube.com" in text or "youtu.be" in text:
            parts = text.rstrip("/").split("/")
            for p in parts:
                if p.startswith("@"):
                    return p[1:].split("?")[0]
        return None

    @staticmethod
    def _extract_channel_id(text: str) -> str | None:
        text = text.strip()
        if text.startswith("UC") and len(text) == 24:
            return text
        if "/channel/" in text:
            seg = text.split("/channel/")[-1].split("?")[0].split("/")[0]
            if seg.startswith("UC"):
                return seg
        return None

    @staticmethod
    def _parse_iso(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    @staticmethod
    def _raise_for_api_error(resp: requests.Response) -> None:
        if resp.ok:
            return
        try:
            err = resp.json()["error"]
            msg = err.get("message", resp.reason)
            errors = err.get("errors", [])
            if errors:
                reason = errors[0].get("reason", "")
                msg = f"{msg} ({reason})"
        except Exception:
            msg = f"HTTP {resp.status_code}"
        raise RuntimeError(f"YouTube API error: {msg}")
