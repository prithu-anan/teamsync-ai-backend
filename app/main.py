from fastapi import FastAPI
from app.routes import health, task , channel

app = FastAPI()

app.include_router(health.router)
app.include_router(task.router)
app.include_router(channel.router)
