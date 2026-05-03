# backend/services/deco.py
import asyncio

async def get_mesh_status():
    # Mocking Deco status based on provided screenshots
    await asyncio.sleep(0.1)
    return {
        "nodes": [
            { "name": "Main - 2F", "online": True, "clients": 11, "rx": "8.8 Mbps", "tx": "263 kbps" },
            { "name": "Elma", "online": True, "clients": 1, "rx": "71 kbps", "tx": "37 kbps" },
            { "name": "Living Room - 1F", "online": True, "clients": 2, "rx": "49 kbps", "tx": "36 kbps" }
        ],
        "totalClients": 14,
        "overallStatus": "Everything looks good"
    }
