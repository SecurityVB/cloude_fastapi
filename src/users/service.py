from functools import wraps

from fastapi import Request, Response
from fastapi.responses import RedirectResponse

from src.users.jwt import TOKEN_LIFETIME, create_jwt, verify_jwt


# request: Request - a mandatory parameter — in the first position in every function
def check_auth():
    def decorator(endpoint):
        @wraps(endpoint)
        async def wrapper(request: Request, *args, **kwargs):
            token = request.cookies.get("access_token")
            if not token:
                return RedirectResponse("/users/login", status_code=303)

            try:
                verify_jwt(token)
            except ValueError:
                return RedirectResponse("/users/login", status_code=303)

            return await endpoint(request, *args, **kwargs)
        return wrapper
    return decorator


def set_auth_cookie(response: Response, request: Request, user_id: int) -> None:
    response.set_cookie(
        key="access_token",
        value=create_jwt(user_id),
        max_age=TOKEN_LIFETIME,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        path="/",
    )
