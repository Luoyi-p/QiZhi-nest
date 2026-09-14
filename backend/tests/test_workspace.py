from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "test.db", demo=False)) as instance:
        yield instance


def new_track(client):
    response = client.post("/api/tracks", json={"title": "学习 Python", "milestones": [{"title": "写一个接口"}, {"title": "写接口测试"}]})
    assert response.status_code == 201
    return response.json()


def test_learning_content_and_session_survive_restart(tmp_path):
    path = tmp_path / "workspace.db"
    with TestClient(create_app(path, demo=False)) as first:
        track = new_track(first)
        note = first.post("/api/entries", json={"kind": "note", "title": "我的第一个接口", "content": "我理解了参数校验。", "track_id": track["id"]})
        assert note.status_code == 201
        assert first.post("/api/sessions", json={"title": "写接口并验证", "minutes": 25, "track_id": track["id"]}).status_code == 201
    with TestClient(create_app(path, demo=False)) as second:
        data = second.get("/api/workspace").json()
        assert data["entries"][0]["content"] == "我理解了参数校验。"
        assert data["entries"][0]["track_id"] == track["id"]
        assert data["sessions"][0]["minutes"] == 25
        assert len(data["tracks"]) == 1


def test_track_progress_and_archive_preserve_related_content(client):
    track = new_track(client)
    assert client.post("/api/entries", json={"kind": "note", "title": "关联笔记", "track_id": track["id"]}).status_code == 201
    response = client.put(f"/api/tracks/{track['id']}", json={"title": track["title"], "archived": True, "milestones": [{"title": "写一个接口", "done": True}, {"title": "写接口测试", "done": False}]})
    assert response.status_code == 200
    assert response.json()["milestones"][0]["done"] is True
    snapshot = client.get("/api/workspace").json()
    assert snapshot["tracks"][0]["archived"] is True
    assert snapshot["entries"][0]["track_id"] == track["id"]


def test_entry_update_archive_and_restore(client):
    entry = client.post("/api/entries", json={"kind": "resource", "title": "文档", "url": "https://example.com/guide"}).json()
    payload = {"kind": "resource", "title": "新标题", "url": entry["url"], "starred": True, "archived": True}
    archived = client.put(f"/api/entries/{entry['id']}", json=payload)
    assert archived.status_code == 200
    assert archived.json()["archived"] is True
    payload["archived"] = False
    restored = client.put(f"/api/entries/{entry['id']}", json=payload).json()
    assert restored["starred"] is True
    assert restored["title"] == "新标题"
    assert restored["archived"] is False


@pytest.mark.parametrize("url", ["javascript:alert(1)", "file:///etc/passwd", "https://", "https://user:secret@example.com"])
def test_rejects_unsafe_resource_urls(client, url):
    response = client.post("/api/entries", json={"kind": "resource", "title": "错误链接", "url": url})
    assert response.status_code == 422
    assert client.get("/api/workspace").json()["entries"] == []


def test_rejects_dangling_relationship_and_invalid_minutes(client):
    assert client.post("/api/entries", json={"kind": "note", "title": "孤立关联", "track_id": "missing"}).status_code == 422
    for minutes in (0, -1, 1441):
        assert client.post("/api/sessions", json={"title": "学习", "minutes": minutes}).status_code == 422
    assert client.put("/api/tracks/missing", json={"title": "不存在"}).status_code == 404


def test_export_import_roundtrip_idempotent_and_non_overwriting(client, tmp_path):
    track = new_track(client)
    client.post("/api/entries", json={"kind": "note", "title": "原始笔记", "track_id": track["id"]})
    client.post("/api/sessions", json={"title": "学习", "minutes": 45, "track_id": track["id"]})
    backup = client.get("/api/export").json()
    with TestClient(create_app(tmp_path / "another.db", demo=False)) as target:
        assert target.post("/api/import", json=backup).json()["imported"] == 3
        assert target.get("/api/export").json() == backup
        entry_id = backup["entries"][0]["id"]
        target.put(f"/api/entries/{entry_id}", json={"kind": "note", "title": "更新后的本地笔记", "track_id": track["id"]})
        assert target.post("/api/import", json=backup).json()["imported"] == 0
        assert target.get("/api/workspace").json()["entries"][0]["title"] == "更新后的本地笔记"


def test_invalid_import_is_atomic(client):
    track = new_track(client)
    backup = client.get("/api/export").json()
    backup["tracks"][0]["id"] = "new-track"
    backup["entries"] = [{"id": "new-note", "kind": "note", "title": "不能部分导入", "track_id": "unknown", "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z"}]
    assert client.post("/api/import", json=backup).status_code == 422
    current = client.get("/api/workspace").json()
    assert len(current["tracks"]) == 1
    assert current["tracks"][0]["id"] == track["id"]
    assert current["entries"] == []
    assert client.post("/api/import", content="not-json").status_code == 422


def test_oversized_import_rejected(client):
    assert client.post("/api/import", content=b" " * (10 * 1024 * 1024 + 1)).status_code == 413


def test_demo_seed_does_not_duplicate_on_restart(tmp_path):
    path = tmp_path / "demo.db"
    with TestClient(create_app(path)) as first:
        data = first.get("/api/workspace").json()
        assert len(data["tracks"]) == 3
        assert len(data["entries"]) == 7
        assert all(e["demo"] for e in data["entries"])
    with TestClient(create_app(path)) as second:
        assert second.get("/api/workspace").json() == data


def test_foreign_web_origin_cannot_write_local_data(client):
    assert client.post("/api/entries", headers={"origin": "https://untrusted.example"}, json={"kind": "note", "title": "外部写入"}).status_code == 403
    assert client.post("/api/entries", headers={"origin": "http://127.0.0.1:5173"}, json={"kind": "note", "title": "自己的笔记"}).status_code == 201


def test_blank_title_and_duplicate_backup_ids_rejected(client):
    assert client.post("/api/entries", json={"kind": "note", "title": "   "}).status_code == 422
    new_track(client)
    backup = client.get("/api/export").json()
    backup["tracks"] *= 2
    assert client.post("/api/import", json=backup).status_code == 422


def test_rejects_foreign_host_header(client):
    assert client.get("/api/export", headers={"host": "untrusted.example"}).status_code == 400


def test_import_rejects_ids_that_cannot_be_addressed_by_routes(client):
    new_track(client)
    backup = client.get("/api/export").json()
    backup["tracks"][0]["id"] = "invalid/route"
    assert client.post("/api/import", json=backup).status_code == 422
