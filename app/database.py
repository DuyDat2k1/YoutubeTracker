from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import ChannelModel, SubscriberSnapshot, VideoModel

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DB_DIR / "tracker.db"


class Database:
    def __init__(self) -> None:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS Channels(
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ChannelId TEXT UNIQUE NOT NULL,
                    Title TEXT NOT NULL,
                    Url TEXT NOT NULL,
                    Subscribers INTEGER NOT NULL DEFAULT 0,
                    VideoCount INTEGER NOT NULL DEFAULT 0,
                    ViewCount INTEGER NOT NULL DEFAULT 0,
                    PublishedAt TEXT,
                    LastChecked TEXT
                );
                CREATE TABLE IF NOT EXISTS SubscriberHistory(
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ChannelDbId INTEGER NOT NULL,
                    CapturedAt TEXT NOT NULL,
                    Subscribers INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS Videos(
                    VideoId TEXT PRIMARY KEY,
                    ChannelDbId INTEGER NOT NULL,
                    Title TEXT NOT NULL,
                    PublishedAt TEXT NOT NULL,
                    Views INTEGER NOT NULL DEFAULT 0,
                    Likes INTEGER NOT NULL DEFAULT 0,
                    Comments INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS VideoHistory(
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    VideoId TEXT NOT NULL,
                    CapturedAt TEXT NOT NULL,
                    Views INTEGER NOT NULL DEFAULT 0,
                    Likes INTEGER NOT NULL DEFAULT 0,
                    Comments INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS SavedUrls(
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Url TEXT UNIQUE NOT NULL,
                    CreatedAt TEXT
                );
                """
            )

    def get_channels(self) -> list[ChannelModel]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT Id,ChannelId,Title,Url,Subscribers,VideoCount,ViewCount,"
                "PublishedAt,LastChecked FROM Channels ORDER BY Title"
            ).fetchall()
        return [
            ChannelModel(
                id=r["Id"],
                channel_id=r["ChannelId"],
                title=r["Title"],
                url=r["Url"],
                subscribers=r["Subscribers"],
                video_count=r["VideoCount"],
                view_count=r["ViewCount"],
                published_at=self._parse_date(r["PublishedAt"]),
                last_checked=self._parse_date(r["LastChecked"]),
            )
            for r in rows
        ]

    def get_channels_by_urls(self, urls: list[str]) -> list[ChannelModel]:
        if not urls:
            return []
        placeholders = ",".join("?" for _ in urls)
        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT Id,ChannelId,Title,Url,Subscribers,VideoCount,ViewCount,"
                f"PublishedAt,LastChecked FROM Channels WHERE Url IN ({placeholders}) "
                f"ORDER BY Title",
                urls,
            ).fetchall()
        return [
            ChannelModel(
                id=r["Id"],
                channel_id=r["ChannelId"],
                title=r["Title"],
                url=r["Url"],
                subscribers=r["Subscribers"],
                video_count=r["VideoCount"],
                view_count=r["ViewCount"],
                published_at=self._parse_date(r["PublishedAt"]),
                last_checked=self._parse_date(r["LastChecked"]),
            )
            for r in rows
        ]

    def search_channels(self, query: str) -> list[ChannelModel]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT Id,ChannelId,Title,Url,Subscribers,VideoCount,ViewCount,"
                "PublishedAt,LastChecked FROM Channels "
                "WHERE Title LIKE ? ORDER BY Title",
                (f"%{query}%",),
            ).fetchall()
        return [
            ChannelModel(
                id=r["Id"],
                channel_id=r["ChannelId"],
                title=r["Title"],
                url=r["Url"],
                subscribers=r["Subscribers"],
                video_count=r["VideoCount"],
                view_count=r["ViewCount"],
                published_at=self._parse_date(r["PublishedAt"]),
                last_checked=self._parse_date(r["LastChecked"]),
            )
            for r in rows
        ]

    def upsert_channel(self, ch: ChannelModel) -> int:
        pub = ch.published_at.isoformat() if ch.published_at else None
        chk = ch.last_checked.isoformat() if ch.last_checked else None
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO Channels(ChannelId,Title,Url,Subscribers,VideoCount,ViewCount,PublishedAt,LastChecked)
                VALUES(?,?,?,?,?,?,?,?)
                ON CONFLICT(ChannelId) DO UPDATE SET
                    Title=excluded.Title, Url=excluded.Url,
                    Subscribers=excluded.Subscribers, VideoCount=excluded.VideoCount,
                    ViewCount=excluded.ViewCount, PublishedAt=excluded.PublishedAt,
                    LastChecked=excluded.LastChecked
                """,
                (ch.channel_id, ch.title, ch.url, ch.subscribers,
                 ch.video_count, ch.view_count, pub, chk),
            )
            row = conn.execute(
                "SELECT Id FROM Channels WHERE ChannelId=?", (ch.channel_id,)
            ).fetchone()
        return row["Id"] if row else 0

    def delete_channel(self, channel_db_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM Videos WHERE ChannelDbId=?", (channel_db_id,))
            conn.execute("DELETE FROM SubscriberHistory WHERE ChannelDbId=?", (channel_db_id,))
            conn.execute("DELETE FROM Channels WHERE Id=?", (channel_db_id,))

    def delete_channel_videos(self, channel_db_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM Videos WHERE ChannelDbId=?", (channel_db_id,))

    def add_snapshot(self, channel_db_id: int, subscribers: int) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO SubscriberHistory(ChannelDbId,CapturedAt,Subscribers) VALUES(?,?,?)",
                (channel_db_id, now, subscribers),
            )

    def get_snapshots(self, channel_db_id: int) -> list[SubscriberSnapshot]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT ChannelDbId,CapturedAt,Subscribers FROM SubscriberHistory "
                "WHERE ChannelDbId=? ORDER BY CapturedAt",
                (channel_db_id,),
            ).fetchall()
        return [
            SubscriberSnapshot(
                channel_db_id=r["ChannelDbId"],
                captured_at=self._parse_date(r["CapturedAt"]),
                subscribers=r["Subscribers"],
            )
            for r in rows
        ]

    def upsert_videos(self, videos: list[VideoModel]) -> None:
        with self._connect() as conn:
            for v in videos:
                pub = v.published_at.isoformat() if v.published_at else ""
                conn.execute(
                    """
                    INSERT INTO Videos(VideoId,ChannelDbId,Title,PublishedAt,Views,Likes,Comments)
                    VALUES(?,?,?,?,?,?,?)
                    ON CONFLICT(VideoId) DO UPDATE SET
                        Title=excluded.Title, PublishedAt=excluded.PublishedAt,
                        Views=excluded.Views, Likes=excluded.Likes, Comments=excluded.Comments
                    """,
                (v.video_id, v.channel_db_id, v.title, pub,
                     v.views, v.likes, v.comments),
                 )

    def add_video_snapshot(self, video_id: str, views: int, likes: int, comments: int) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO VideoHistory(VideoId,CapturedAt,Views,Likes,Comments) VALUES(?,?,?,?,?)",
                (video_id, now, views, likes, comments),
            )

    def has_today_snapshot(self, video_id: str) -> bool:
        today = datetime.now(timezone.utc).date().isoformat()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT Id FROM VideoHistory WHERE VideoId=? AND CapturedAt >= ?",
                (video_id, today),
            ).fetchone()
        return row is not None

    def get_video_history(self, video_id: str, days: int = 7) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT CapturedAt,Views,Likes,Comments FROM VideoHistory "
                "WHERE VideoId=? AND CapturedAt >= datetime('now', ?) ORDER BY CapturedAt",
                (video_id, f"-{days} days"),
            ).fetchall()
        return [
            {
                "captured_at": self._parse_date(r["CapturedAt"]),
                "views": r["Views"],
                "likes": r["Likes"],
                "comments": r["Comments"],
            }
            for r in rows
        ]

    def get_latest_videos(self, channel_db_id: int, take: int = 10) -> list[VideoModel]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT VideoId,ChannelDbId,Title,PublishedAt,Views,Likes,Comments "
                "FROM Videos WHERE ChannelDbId=? ORDER BY PublishedAt DESC LIMIT ?",
                (channel_db_id, take),
            ).fetchall()
        return [
            VideoModel(
                video_id=r["VideoId"],
                channel_db_id=r["ChannelDbId"],
                title=r["Title"],
                published_at=self._parse_date(r["PublishedAt"]),
                views=r["Views"],
                likes=r["Likes"],
                comments=r["Comments"],
            )
            for r in rows
        ]

    def add_saved_url(self, url: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO SavedUrls(Url,CreatedAt) VALUES(?,?)",
                (url, now),
            )

    def get_saved_urls(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT Url FROM SavedUrls ORDER BY CreatedAt").fetchall()
        return [r["Url"] for r in rows]

    def remove_saved_url(self, url: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM SavedUrls WHERE Url=?", (url,))

    def clear_saved_urls(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM SavedUrls")

    @staticmethod
    def _parse_date(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
