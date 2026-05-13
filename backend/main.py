import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from services.mikrotik import get_isp_status, get_router_health
from services.deco import get_mesh_status
from services.outage_logger import get_outage_logs
from services.telegram_bot import start_bot, stop_bot

# Global cache to hold the latest data
app_cache = {
    "isps": {},
    "mesh": {"nodes": [], "totalClients": "---", "overallStatus": "Loading..."},
    "router_health": {"cpu": "---", "ram": "---", "temp": "---", "uptime": "---"},
    "outages": [],
    "timestamp": None
}

async def poll_hardware():
    while True:
        try:
            isps = await get_isp_status()
            mesh = await get_mesh_status()
            router_health = await get_router_health()
            outages = get_outage_logs()
            
            app_cache["isps"] = isps
            app_cache["mesh"] = mesh
            app_cache["router_health"] = router_health
            app_cache["outages"] = outages
            app_cache["timestamp"] = datetime.utcnow().isoformat() + "Z"
        except Exception as e:
            print(f"Background polling error: {e}")
        # Wait 5 seconds before fetching again
        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the background polling task when the server starts
    polling_task = asyncio.create_task(poll_hardware())
    # Start the Telegram Bot listener
    bot_task = asyncio.create_task(start_bot())
    yield
    # Clean up the task when the server shuts down
    polling_task.cancel()
    await stop_bot()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
async def read_status():
    # Instantly return the cached data instead of waiting for the hardware
    if not app_cache["timestamp"]:
        # Fallback if accessed before the first poll finishes
        app_cache["timestamp"] = datetime.utcnow().isoformat() + "Z"
    return app_cache
