from fastapi import Request, Response
from src.users.jwt import TOKEN_LIFETIME, create_jwt

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