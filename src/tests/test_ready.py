import json
from types import SimpleNamespace

import api
import database


class Engine:
    def __init__(self, reachable):
        self.reachable = reachable

    def connect(self):
        if not self.reachable:
            raise OSError("unreachable")
        return self

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, query):
        pass


def s3_client(reachable):
    def list_buckets():
        if not reachable:
            raise OSError("unreachable")
    return SimpleNamespace(list_buckets=list_buckets)


def ready(monkeypatch, postgres, s3):
    monkeypatch.setattr(database, "ready_engine", Engine(postgres))
    request = SimpleNamespace(app=SimpleNamespace(ready_s3client=s3_client(s3)))
    response = api.ready(request)
    return response.status_code, json.loads(response.body)


def test_ready(monkeypatch):
    assert ready(monkeypatch, True, True) == (
        200, {"status": "ok", "postgres": "ok", "s3": "ok"})


def test_not_ready_names_the_failing_dependency(monkeypatch):
    assert ready(monkeypatch, True, False) == (
        503, {"status": "not ready", "postgres": "ok", "s3": "unreachable"})
    assert ready(monkeypatch, False, True) == (
        503, {"status": "not ready", "postgres": "unreachable", "s3": "ok"})
