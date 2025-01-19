from fastapi import APIRouter, HTTPException, Depends
from app.api.endpoints import openai, medicare, reservations
# from app.api.dependencies import get_api_key

router = APIRouter()

# router.include_router(
#     qr_extractor.router,
#     prefix="/qr",
#     tags=["QR Processing"],
#     dependencies=[Depends(get_api_key)]
# )

router.include_router(
    openai.router,
    prefix="/openai",
    tags=["General LLM"]
)

router.include_router(
    medicare.router,
    prefix="/medicare",
    tags=["Medicare"]
)

router.include_router(
    reservations.router,
    prefix="/reservations",
    tags=["Reservations"]
)
