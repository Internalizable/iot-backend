from fastapi import FastAPI
from routers import sensors, users

app = FastAPI()

app.include_router(sensors.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the IOT API! 🚀"}
