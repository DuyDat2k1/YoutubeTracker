from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChannelModel:
    id: int = 0
    channel_id: str = ""
    title: str = ""
    url: str = ""
    subscribers: int = 0
    video_count: int = 0
    view_count: int = 0
    published_at: datetime | None = None
    last_checked: datetime | None = None


@dataclass
class VideoModel:
    video_id: str = ""
    channel_db_id: int = 0
    title: str = ""
    published_at: datetime | None = None
    views: int = 0
    likes: int = 0
    comments: int = 0


@dataclass
class SubscriberSnapshot:
    channel_db_id: int = 0
    captured_at: datetime | None = None
    subscribers: int = 0
