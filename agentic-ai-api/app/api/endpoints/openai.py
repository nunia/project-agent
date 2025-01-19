from fastapi import APIRouter, FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
from typing import Optional
import os
# from app.core.config import openai_api_key
# from app.core.logging_config import logger  # Import logger from logging_config
# from app.core.database import SessionLocal
from app.services.openai_service import (
    complete_chat,
    process_agent3,
    process_agent4,
    process_agent5
)

router = APIRouter()

@router.post("/ask")
async def ask(message: str):
    completion = complete_chat(message)
    if completion:
        return {"Nunia.AI": completion}
    else:
        return {"error": "Failed to complete chat."}

# @router.post("/agent1")
# async def agent1(message: str):
#     completion = await process_agent1(message)
#     if completion:
#         return {"Nunia.AI": completion}
#     else:
#         return {"error": "Failed to complete chat."}

# @router.post("/agent2")
# async def agent2(message: str):
#     completion = await process_agent2(message)
#     if completion:
#         return {"Nunia.AI": completion}
#     else:
#         return {"error": "Failed to complete chat."}

@router.post("/agent3")
async def agent3(message: str):
    completion = await process_agent3(message)
    if completion:
        return {"Nunia.AI": completion}
    else:
        return {"error": "Failed to complete chat."}

@router.post("/agent4")
async def agent3(message: str):
    completion = await process_agent4(message)
    if completion:
        return {"Nunia.AI": completion}
    else:
        return {"error": "Failed to complete chat."}

@router.post("/agent5")
async def agent3(message: str):
    completion = await process_agent5(message)
    if completion:
        return {"Nunia.AI": completion}
    else:
        return {"error": "Failed to complete chat."}