
from functools import wraps
import jwt

from django.conf import settings

from django.shortcuts import redirect

from .models import Account


def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get("jwt_token")

        if not token:
            print("No JWT token found in cookies.")
            return redirect("login")

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )

            
            user = Account.objects.get(id=payload['id'])
            print("User from JWT:", user.username)
            if not user:
                print("User not found in database.")
                request.COOKIES.pop("access_token", None)
                return redirect("login")

        except (
            jwt.InvalidTokenError,
            KeyError,
            TypeError,
        ):
            print("Invalid JWT token or missing user ID.")
            request.COOKIES.pop("access_token", None)
            return redirect("login")

        request.jwt_user = user
        return view_func(request, *args, **kwargs)

    return wrapper
