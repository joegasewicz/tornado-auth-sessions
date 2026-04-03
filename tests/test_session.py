from unittest.mock import Mock, patch

from tornado_auth_sessions.session import TornadoAuthSessionMixin


class DummyApplication:
    def __init__(self):
        self.settings = {
            "redis_host": {
                "host": "localhost",
                "port": 6379,
                "db": 0,
                "password": None,
                "decode_responses": True,
            }
        }


class DummyHandler(TornadoAuthSessionMixin):
    def __init__(self):
        self.application = DummyApplication()
        self._secure_cookie = None
        self.client = None
        self.set_secure_cookie = Mock()
        self.get_secure_cookie = Mock()


class TestTornadoAuthSessionMixin:

    def test_init_session_creates_client_and_initializes_it(self):
        handler = DummyHandler()

        mock_client = Mock()
        mock_client.r = Mock()

        with patch("tornado_auth_sessions.session.RedisClient", return_value=mock_client) as mock_redis_client:
            handler._init_session()

        mock_redis_client.assert_called_once_with(
            host="localhost",
            port=6379,
            db=0,
            password=None,
            decode_responses=True,
        )
        assert handler.client is mock_client

    def test_get_session_returns_none_when_cookie_missing(self):
        handler = DummyHandler()
        handler.get_secure_cookie.return_value = None

        mock_client = Mock()
        mock_client.r = Mock()

        with patch("tornado_auth_sessions.session.RedisClient", return_value=mock_client):
            result = handler.get_session()

        assert result is None
        handler.get_secure_cookie.assert_called_once_with("session_id")
        mock_client.get_session_id.assert_not_called()

    def test_get_session_returns_user_id_from_client(self):
        handler = DummyHandler()
        handler.get_secure_cookie.return_value = b"abc123"

        mock_client = Mock()
        mock_client.r = Mock()
        mock_client.get_session_id.return_value = "42"

        with patch("tornado_auth_sessions.session.RedisClient", return_value=mock_client):
            result = handler.get_session()

        assert result == "42"
        handler.get_secure_cookie.assert_called_once_with("session_id")
        mock_client.get_session_id.assert_called_once_with(b"abc123")

    def test_set_session_stores_session_and_sets_cookie(self):
        handler = DummyHandler()

        mock_client = Mock()
        mock_client.r = Mock()
        mock_client.gen_session_id_and_store_in_redis.return_value = "generated-session-id"

        with patch("tornado_auth_sessions.session.RedisClient", return_value=mock_client):
            handler.set_session(123, is_secure=False)

        mock_client.gen_session_id_and_store_in_redis.assert_called_once_with(123)
        handler.set_secure_cookie.assert_called_once_with(
            "session_id",
            "generated-session-id",
            httponly=True,
            secure=False,
            expires_days=7,
        )

    def test_remove_session_returns_none_when_cookie_missing(self):
        handler = DummyHandler()
        handler.get_secure_cookie.return_value = None
        handler.client = Mock()

        result = handler.remove_session(123)

        assert result is None
        handler.get_secure_cookie.assert_called_once_with("session_id")
        handler.client.remove_session_id.assert_not_called()

    def test_remove_session_deletes_session_from_client(self):
        handler = DummyHandler()
        handler.get_secure_cookie.return_value = "abc123"
        handler.client = Mock()

        result = handler.remove_session(123)

        assert result is None
        handler.get_secure_cookie.assert_called_once_with("session_id")
        handler.client.remove_session_id.assert_called_once_with("abc123")

    def test_init_session_reuses_existing_client(self):
        handler = DummyHandler()
        existing_client = Mock()
        existing_client.r = Mock()
        handler.client = existing_client

        with patch("tornado_auth_sessions.session.RedisClient") as mock_redis_client:
            handler._init_session()

        mock_redis_client.assert_not_called()
        assert handler.client is existing_client