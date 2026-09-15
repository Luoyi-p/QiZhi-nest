from datetime import datetime
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Milestone(Model):
    title: str = Field(min_length=1, max_length=200)
    done: bool = False


class TrackInput(Model):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)
    color: Literal["green", "blue", "orange", "purple"] = "green"
    milestones: list[Milestone] = Field(default_factory=list, max_length=50)
    archived: bool = False


class Track(TrackInput):
    id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    created_at: datetime
    demo: bool = False


class EntryInput(Model):
    kind: Literal["resource", "note", "project"]
    title: str = Field(min_length=1, max_length=180)
    content: Annotated[str, StringConstraints(strip_whitespace=False)] = Field(default="", max_length=50000)
    url: str = Field(default="", max_length=2000)
    tags: list[str] = Field(default_factory=list, max_length=12)
    track_id: str | None = Field(default=None, max_length=100)
    starred: bool = False
    archived: bool = False
    status: Literal["inbox", "active", "done"] = "inbox"

    @field_validator("url")
    @classmethod
    def safe_url(cls, value: str) -> str:
        if value:
            parsed = urlsplit(value)
            if parsed.scheme not in ("https", "http") or not parsed.hostname or parsed.username or parsed.password:
                raise ValueError("链接必须是有效的 http 或 https 地址，且不能包含账号密码")
        return value

    @field_validator("tags")
    @classmethod
    def valid_tags(cls, values: list[str]) -> list[str]:
        tags = list(dict.fromkeys(tag.strip() for tag in values if tag.strip()))
        if any(len(tag) > 40 for tag in tags):
            raise ValueError("标签不能超过 40 个字符")
        return tags


class Entry(EntryInput):
    id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    created_at: datetime
    updated_at: datetime
    demo: bool = False


class SessionInput(Model):
    title: str = Field(min_length=1, max_length=180)
    minutes: int = Field(ge=1, le=1440)
    track_id: str | None = Field(default=None, max_length=100)


class Session(SessionInput):
    id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    created_at: datetime
    demo: bool = False


class Backup(Model):
    version: Literal[1] = 1
    tracks: list[Track] = Field(default_factory=list, max_length=1000)
    entries: list[Entry] = Field(default_factory=list, max_length=10000)
    sessions: list[Session] = Field(default_factory=list, max_length=20000)
