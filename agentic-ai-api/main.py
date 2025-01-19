from fastapi import FastAPI
from app.api import routers
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os

# Load environment variables from .env file
load_dotenv()

# Optionally set up logging (uncomment if you have a logging setup)
# from app.core.logging_config import setup_logging
# setup_logging()  # Call logging setup function

app = FastAPI(title="Nunia.AgenticAI.API")

# Allow all origins (not recommended for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],   # Allow all headers
)

# Include routers/endpoints from the app/api directory
app.include_router(routers.router)

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    except KeyboardInterrupt:
        print("Interrupted. Exiting gracefully...")
