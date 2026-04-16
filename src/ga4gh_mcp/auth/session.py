"""Per-user session management with isolation."""

from __future__ import annotations

import time


class Session:
    """Isolated per-user session."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.created_at = time.time()
        self.last_accessed = time.time()

    def touch(self) -> None:
        self.last_accessed = time.time()


class SessionManager:
    """Manages isolated sessions per user with TTL and max capacity."""

    def __init__(self, ttl_minutes: int, max_sessions: int):
        self._ttl_seconds = ttl_minutes * 60
        self._max_sessions = max_sessions
        self._sessions: dict[str, Session] = {}

    def get_or_create(self, user_id: str) -> Session:
        if user_id in self._sessions:
            session = self._sessions[user_id]
            session.touch()
            return session

        if len(self._sessions) >= self._max_sessions:
            self._evict_oldest()

        session = Session(user_id)
        self._sessions[user_id] = session
        return session

    def remove(self, user_id: str) -> None:
        self._sessions.pop(user_id, None)

    def cleanup_expired(self) -> None:
        now = time.time()
        expired = [
            uid for uid, s in self._sessions.items()
            if (now - s.last_accessed) > self._ttl_seconds
        ]
        for uid in expired:
            del self._sessions[uid]

    def _evict_oldest(self) -> None:
        if not self._sessions:
            return
        oldest = min(self._sessions, key=lambda uid: self._sessions[uid].last_accessed)
        del self._sessions[oldest]
