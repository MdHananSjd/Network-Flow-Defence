from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
from backend.api.routes import game # Imports the game router

app = FastAPI(title="Network Flow Defense API")

# Dynamic CORS Configuration
FRONTEND_ORIGIN = config('FRONTEND_URL', default='http://localhost:5173')
ORIGINS = FRONTEND_ORIGIN.split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Game Router
app.include_router(game.router, prefix="/api") 

# Health Check
@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "pong"}

