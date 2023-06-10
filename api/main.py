from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from internal.controllers import user, chat
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(router=user.router)
app.include_router(router=chat.router)