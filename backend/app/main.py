import os
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .db import Database
from .models import Backup, Entry, EntryInput, Session, SessionInput, Track, TrackInput
from .seed import seed_demo


def create_app(db_path: Path | None = None, demo: bool = True) -> FastAPI:
    api = FastAPI(title="Nest 栖知", version="0.1.0")
    api.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"]
    )
    path = db_path or Path(os.environ.get(
        "NEST_DB_PATH", Path(__file__).resolve().parents[2] / "data" / "nest.db"
    ))
    db = Database(path)
    if demo:
        seed_demo(db)

    @api.middleware("http")
    async def local_writes(request: Request, call_next):
        # Reject browser writes from other sites; this is not authentication.
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            allowed = {
                "http://127.0.0.1:5173",
                "http://localhost:5173",
                "http://127.0.0.1:8000",
                "http://localhost:8000",
            }
            origin = request.headers.get("origin")
            if origin and origin not in allowed:
                return JSONResponse({"detail": "不允许此来源修改本地数据"}, status_code=403)
        return await call_next(request)

    def require(collection: str, identifier: str):
        record = db.get(collection, identifier)
        if not record:
            raise HTTPException(404, "记录不存在")
        return record

    def check_track(track_id: str | None):
        if track_id and not db.get("tracks", track_id):
            raise HTTPException(422, "关联的学习路线不存在")

    @api.get("/api/health")
    def health():
        return {"status": "ok"}

    @api.get("/api/workspace", response_model=Backup)
    def workspace():
        return db.snapshot()

    @api.post("/api/tracks", response_model=Track, status_code=201)
    def create_track(data: TrackInput):
        record = Track(**data.model_dump(), id=str(uuid4()), created_at=datetime.now(timezone.utc))
        return db.save("tracks", record.model_dump(mode="json"))

    @api.put("/api/tracks/{identifier}", response_model=Track)
    def update_track(identifier: str, data: TrackInput):
        previous = require("tracks", identifier)
        record = {**previous, **data.model_dump(mode="json")}
        return db.save("tracks", record)

    @api.post("/api/entries", response_model=Entry, status_code=201)
    def create_entry(data: EntryInput):
        check_track(data.track_id)
        now = datetime.now(timezone.utc)
        record = Entry(**data.model_dump(), id=str(uuid4()), created_at=now, updated_at=now)
        return db.save("entries", record.model_dump(mode="json"))

    @api.put("/api/entries/{identifier}", response_model=Entry)
    def update_entry(identifier: str, data: EntryInput):
        previous = require("entries", identifier)
        check_track(data.track_id)
        return db.save("entries", {
            **previous,
            **data.model_dump(mode="json"),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })

    @api.post("/api/sessions", response_model=Session, status_code=201)
    def create_session(data: SessionInput):
        check_track(data.track_id)
        record = Session(**data.model_dump(), id=str(uuid4()), created_at=datetime.now(timezone.utc))
        return db.save("sessions", record.model_dump(mode="json"))

    @api.get("/api/export", response_model=Backup)
    def export():
        return db.snapshot()

    @api.post("/api/import")
    async def import_backup(request: Request):
        # Stream before parsing, so an oversized upload cannot consume unbounded memory.
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 10 * 1024 * 1024:
                raise HTTPException(413, "备份文件不能超过 10 MB")
        try:
            backup = Backup.model_validate_json(bytes(body))
        except ValueError:
            raise HTTPException(422, "备份格式无效，请导入栖知导出的 JSON 文件")
        for collection in (backup.tracks, backup.entries, backup.sessions):
            ids = [item.id for item in collection]
            if len(ids) != len(set(ids)):
                raise HTTPException(422, "备份中包含重复 ID")
        known_tracks = {t["id"] for t in db.all("tracks")} | {t.id for t in backup.tracks}
        if any(
            item.track_id and item.track_id not in known_tracks
            for item in [*backup.entries, *backup.sessions]
        ):
            raise HTTPException(422, "备份包含不存在的学习路线关联")
        count = db.merge(backup.model_dump(mode="json"))
        return {"imported": count, "message": "已合并导入；相同 ID 的本地记录保持不变"}

    static_dir = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if static_dir.exists():
        api.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
    return api


app = create_app()
