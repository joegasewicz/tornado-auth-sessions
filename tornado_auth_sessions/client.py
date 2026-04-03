import secrets
from abc import ABC, abstractmethod

import redis

from tornado_auth_sessions.log import log


class Client(ABC):

    @abstractmethod
    def init_client(self) -> None:
        ...

    @abstractmethod
    def get_session_id(self, session_id: bytes) -> str | None:
        ...

    @abstractmethod
    def gen_session_id_and_store_in_redis(self, user_id: int) -> str:
        ...

    @abstractmethod
    def remove_session_id(self, session_id: str) -> None:
        ...


class RedisClient(Client):

    r: redis.Redis

    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str = None,
        decode_responses: bool = None,
    ):
        super().__init__()
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.decode_responses = decode_responses

    def init_client(self) -> None:
        """
        Initialises the Redis client
        Let the connection raise a `redis.exceptions.ConnectionError` for the end user
        :return:
        """
        self.r = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=self.decode_responses,
        )
        is_conn = self.r.ping()
        if is_conn:
            log.debug("[TORNADO SESSION]: Successfully connected to the Redis client.")
        else:
            log.error("[TORNADO SESSION]: Connection to Redis was unsuccessful")

    def get_session_id(self, session_id: bytes) -> str | None:
        """
        :return:
        """
        if not session_id:
            return None
        session_id = session_id.decode()
        return self.r.get(self._create_session_key(session_id))

    def gen_session_id_and_store_in_redis(self, user_id: int) -> str:
        session_id = secrets.token_urlsafe(32)
        session_key = self._create_session_key(session_id)
        log.debug(f"New session key created: {session_key}")
        self.r.setex(session_key, 60 * 60 * 24 * 7, user_id)
        return session_id

    def remove_session_id(self, session_id: str) -> None:
        self.r.delete(self._create_session_key(session_id))

    def _create_session_key(self, session_id: str) -> str:
        return f"session:{session_id}"
