from fastapi import APIRouter, Request

CatalogsRouter = APIRouter(
    prefix="/catalogs",
)

@CatalogsRouter.get("/", tags=["catalogs"])
async def get_directories(request: Request):
    pass