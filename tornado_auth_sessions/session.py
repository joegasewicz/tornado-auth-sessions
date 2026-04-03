from app.middleware.client import RedisClient


class TornadoAuthSessionMixin:
    """
    Base handler with session support via TornadoAuthSessionMixin.

    This mixin requires Redis configuration to be provided via
    Tornado application settings.

    Expected application settings::

        tornado.web.Application(
            handlers,
            redis_host={
                "host": "localhost",
                "port": 6379,
                "db": 0,
                "password": None,
                "decode_responses": True,
            },
        )

    The mixin will lazily initialise a RedisClient using this configuration
    on first use.

    Provides helper methods:
        - get_session()
        - set_session(user_id)
        - remove_session(user_id)

    Example::

        import tornado

        class DashboardHandler(BaseHandler):
            def get(self):
                user_id = self.get_session()
                if not user_id:
                    self.redirect("/login")
                    return

                self.write(f"Welcome user {user_id}")

        class LoginHandler(BaseHandler):
            def post(self):
                # authenticate user...
                self.set_session(user.id)
                self.redirect("/dashboard")

        class LogoutHandler(BaseHandler):
            def post(self):
                self.remove_session(user.id)
                self.redirect("/")

    """

    def _init_session(self):
        if not hasattr(self, "client") or self.client is None:
            redis_host = self.application.settings.get("redis_host")
            self.client = RedisClient(**redis_host)
            if not hasattr(self.client, "r"):
                self.client.init_client()

    def get_session(self) -> str | None:
        """
        :return: user_id if session exists, else None

        Example::

            user_id = self.get_session()
            if user_id:
                print("Logged in:", user_id)
        """
        self._init_session()
        session_id = self.get_secure_cookie("session_id")
        if not session_id:
            return None
        session_id = self.client.get_session_id(session_id)
        return session_id

    def set_session(self, user_id: int, is_secure: bool = True):
        """
        :param user_id: user id to store in session
        :param is_secure: whether cookie should be HTTPS only
        :return: None

        Example::

            self.set_session(user.id)
        """
        self._init_session()
        session_id = self.client.gen_session_id_and_store_in_redis(user_id)
        self.set_secure_cookie(
            "session_id",
            session_id,
            httponly=True,
            secure=is_secure,
            expires_days=7,
        )

    def remove_session(self, user_id: int) -> None:
        """
        :param user_id: user id (optional, for context/logging)
        :return: None

        Example::

            self.remove_session(user.id)
        """
        session_id = self.get_secure_cookie("session_id")
        if not session_id:
            return None
        self.client.remove_session_id(session_id)
        return None
