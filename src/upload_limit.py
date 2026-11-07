from fastapi import HTTPException
from starlette.datastructures import Headers
from starlette.responses import JSONResponse


class UploadSizeLimit:
    def __init__(self, app, max_bytes: int):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] != "POST" or scope["path"] not in {
            "/catalogs/upload", "/sharing/upload"
        }:
            return await self.app(scope, receive, send)

        detail = "Превышен лимит размера загрузки"
        length = Headers(scope=scope).get("content-length")
        if length and length.isdigit() and int(length) > self.max_bytes:
            return await JSONResponse({"detail": detail}, status_code=413)(scope, receive, send)

        received = 0

        async def limited_receive():
            nonlocal received
            message = await receive()
            received += len(message.get("body", b""))
            if received > self.max_bytes:
                raise HTTPException(413, detail)
            return message

        await self.app(scope, limited_receive, send)
