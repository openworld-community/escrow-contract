import os
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from internal.controllers import user, chat

from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router=user.router)
app.include_router(router=chat.router)

@app.get("/env/{key}")
async def get_env(key: str):
    return os.getenv(key)