from fastapi import FastAPI
from internal.controllers import user
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(router=user.router)
