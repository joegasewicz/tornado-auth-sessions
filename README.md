# Tornado Auth Sessions

Simple, secure Redis-backed session mixin for Tornado.

## Installation

```bash
pip install tornado-auth-sessions
```
---

## Setup

Configure Redis via Tornado application settings:

```python
import tornado.web

app = tornado.web.Application(
    handlers,
    redis_host={
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": None,
        "decode_responses": True,
    },
    cookie_secret="YOUR_SECRET_KEY",
)
```

---

## Usage

Create a base handler:
```python
import tornado
from tornado_auth_sessions import TornadoSessionsMixin


class BaseHandler(
    TornadoSessionsMixin,
    tornado.web.RequestHandler,
):
    pass 
```

---

## Example
### Login

```python
class LoginHandler(BaseHandler):
    def post(self):
        # authenticate user...
        self.set_session(user.id)
        self.redirect("/dashboard")
```

### Protected route

```python
class DashboardHandler(BaseHandler):
    def get(self):
        user_id = self.get_session()
        if not user_id:
            self.redirect("/login")
            return

        self.write(f"Welcome user {user_id}") 
```

### Logout

```python
class LogoutHandler(BaseHandler):
    def post(self):
        self.remove_session(user.id)
        self.redirect("/")
```

## Authentication (Tornado Native)

This library integrates seamlessly with Tornado’s built-in authentication system via `get_current_user`.

Add this to your base handler:

```python
import tornado

class DashboardHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        user_id = self.current_user
        self.write(f"User: {user_id}")
```

---

## Security notes
- Uses Tornado set_secure_cookie (signed, tamper-proof)
- Always use HTTPS in production
- Set secure=True for cookies
- Use strong cookie_secret
- Pair with CSRF protection for forms