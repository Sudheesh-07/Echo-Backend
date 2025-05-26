from fastapi import FastAPI
from auth.router import router as auth_router

app = FastAPI()
@app.get("/")
async def root():
    return {"message": "API is running"}
app.include_router(auth_router)
