from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import certifi

app = FastAPI()
load_dotenv()

ca = certifi.where()
origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Connect to MongoDB
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI, tls=True, tlsCAFile=ca)
database = client.protest_db
protests_collection = database.get_collection("protests")

class BrowserInfo(BaseModel):
    userAgent: str
    appVersion: str
    platform: str
    language: str

@app.post("/api/protest")
async def protest(browser_info: BrowserInfo, request: Request):
    client_host = request.client.host

    # Check if the user has already protestd
    existing_protest = protests_collection.find_one({"ip": client_host})
    if existing_protest:
        raise HTTPException(status_code=400, detail="User has already protestd")

    protest_data = {
        "userAgent": browser_info.userAgent,
        "appVersion": browser_info.appVersion,
        "platform": browser_info.platform,
        "language": browser_info.language,
        "ip": client_host
    }

    # Insert the protest data into the database
    protests_collection.insert_one(protest_data)
    return {"message": "protest recorded"}

@app.get("/api/protest-count")
async def get_protest_count():
    protest_count = protests_collection.count_documents({})
    return {"count": protest_count}
