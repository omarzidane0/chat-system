from http.cookies import SimpleCookie

import jwt
from channels.db import database_sync_to_async
from django.conf import settings

from accounts.models import Account


@database_sync_to_async
def get_account(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return Account.objects.get(id=payload['id'])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError, Account.DoesNotExist):
        return None


class JwtAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        headers = dict(scope.get('headers', []))
        cookie = SimpleCookie()
        try:
            cookie.load(headers.get(b'cookie', b'').decode('latin1'))
            token = cookie['jwt_token'].value
        except (KeyError, ValueError):
            token = None

        user = await get_account(token) if token else None
        return await self.app({**scope, 'user': user}, receive, send)