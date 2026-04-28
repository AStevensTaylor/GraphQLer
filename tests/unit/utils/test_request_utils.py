from graphqler import config
from graphqler.utils import request_utils


def test_create_new_session_applies_proxy_settings(monkeypatch):
    monkeypatch.setattr(config, "PROXY", "http://127.0.0.1:8080")
    monkeypatch.setattr(config, "CUSTOM_HEADERS", {})
    monkeypatch.setattr(config, "AUTHORIZATION", None)

    session = request_utils.create_new_session()
    try:
        assert session.proxies["http"] == "http://127.0.0.1:8080"
        assert session.verify is False
    finally:
        session.close()