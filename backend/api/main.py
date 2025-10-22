#main entry point for the FastAPI application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from decouple import config #reading variables from .env

app = FastAPI(title="Network Defence API")

#Dynamic CORS Configuration
FRONTEND_ORIGIN = config('FRONTEND_URL', default = 'http://localhost:5173')
ORIGINS = FRONTEND_ORIGIN.split(',') #making it a list for fastpai

app.add_middleware(
    CORSMiddleware,
    allow_origins = ORIGINS,
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)

#health check
@app.get("/ping")
async def ping():
    return {
        "status":"ok", 
        "message":"pong"
    }