from fastapi import FastAPI
from dotenv import load_dotenv
import os

loaded = load_dotenv(".env")
print("Loaded:", loaded)
print("APP_NAME:", os.getenv("APP_NAME"))
print("APP_VERSION:", os.getenv("APP_VERSION"))

from routes import base

app = FastAPI()
app.include_router(base.base_router)