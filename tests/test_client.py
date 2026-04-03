from unittest.mock import Mock, patch

import redis

from tornado_auth_sessions.client import RedisClient


class TestClient:

    def test_init_client_sets_redis_instance_and_pings(self):
        client = RedisClient(
            host="localhost",
            port=6379,
            db=0,
            password=None,
            decode_responses=True,
        )

        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True

        with patch("tornado_auth_sessions.client.redis.Redis", return_value=mock_redis_instance) as mock_redis:
            client.init_client()

        mock_redis.assert_called_once_with(
            host="localhost",
            port=6379,
            db=0,
            password=None,
            decode_responses=True,
        )
        mock_redis_instance.ping.assert_called_once()
        assert client.r is mock_redis_instance

    def test_get_session_id_returns_none_when_session_id_missing(self):
        client = RedisClient()
        client.r = Mock()

        result = client.get_session_id(None)

        assert result is None
        client.r.get.assert_not_called()

    def test_get_session_id_decodes_cookie_and_fetches_from_redis(self):
        client = RedisClient()
        client.r = Mock()
        client.r.get.return_value = "42"

        result = client.get_session_id(b"abc123")

        assert result == "42"
        client.r.get.assert_called_once_with("session:abc123")

    def test_gen_session_id_and_store_in_redis_returns_session_id(self):
        client = RedisClient()
        client.r = Mock()

        with patch("tornado_auth_sessions.client.secrets.token_urlsafe", return_value="generated-session-id"):
            result = client.gen_session_id_and_store_in_redis(123)

        assert result == "generated-session-id"
        client.r.setex.assert_called_once_with(
            "session:generated-session-id",
            60 * 60 * 24 * 7,
            123,
        )

    def test_remove_session_id_deletes_redis_key(self):
        client = RedisClient()
        client.r = Mock()

        client.remove_session_id("abc123")

        client.r.delete.assert_called_once_with("session:abc123")

    def test_create_session_key(self):
        client = RedisClient()

        result = client._create_session_key("abc123")

        assert result == "session:abc123"

    def test_init_client_raises_connection_error_when_ping_fails(self):
        client = RedisClient()

        mock_redis_instance = Mock()
        mock_redis_instance.ping.side_effect = redis.exceptions.ConnectionError("boom")

        with patch("tornado_auth_sessions.client.redis.Redis", return_value=mock_redis_instance):
            try:
                client.init_client()
                assert False, "Expected ConnectionError to be raised"
            except redis.exceptions.ConnectionError:
                pass