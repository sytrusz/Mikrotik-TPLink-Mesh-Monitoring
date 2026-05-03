from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from services.mikrotik import get_isp_status
from services.deco import get_mesh_status

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
async def read_status():
    isps = await get_isp_status()
    mesh = await get_mesh_status()
    return {
        "isps": isps,
        "mesh": mesh,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
