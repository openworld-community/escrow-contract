from fastapi import FastAPI
from internal.routers import user


app = FastAPI()

app.include_router(router=user.router)
