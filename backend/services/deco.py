# backend/services/deco.py
import asyncio
import os
import subprocess
from tplinkrouterc6u import TplinkRouter
from dotenv import load_dotenv

load_dotenv()

DECO_HOST = os.getenv("DECO_HOST", "192.168.68.1")
DECO_PASS = os.getenv("DECO_PASS", "")

NODE1_IP = os.getenv("NODE1_IP", "")
NODE1_NAME = os.getenv("NODE1_NAME", "Main Node")

NODE2_IP = os.getenv("NODE2_IP", "")
NODE2_NAME = os.getenv("NODE2_NAME", "Node 2")

NODE3_IP = os.getenv("NODE3_IP", "")
NODE3_NAME = os.getenv("NODE3_NAME", "Node 3")

def sync_ping(ip):
    if not ip or ip == "0.0.0.0":
        return False
    try:
        result = subprocess.run(
            ['ping', '-n', '1', '-w', '1000', ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return result.returncode == 0
    except Exception:
        return False

async def ping(ip):
    return await asyncio.to_thread(sync_ping, ip)

async def get_mesh_status():
    nodes = []
    total_clients = 0
    api_success = False
    
    if DECO_PASS:
        try:
            router = TplinkRouter(DECO_HOST, DECO_PASS)
            if await router.authorize():
                status = await router.get_status()
                total_clients = status.all_clients_count
                nodes.append({
                    "name": NODE1_NAME,
                    "online": True,
                    "clients": total_clients,
                    "rx": "---",
                    "tx": "---"
                })
                api_success = True
                await router.logout()
        except Exception:
            pass

    if not api_success:
        is_up = await ping(DECO_HOST)
        nodes.append({
            "name": NODE1_NAME,
            "online": is_up,
            "clients": "---",
            "rx": "---",
            "tx": "---"
        })

    node2_up, node3_up = await asyncio.gather(
        ping(NODE2_IP),
        ping(NODE3_IP)
    )

    nodes.append({"name": NODE2_NAME, "online": node2_up, "clients": "---", "rx": "---", "tx": "---"})
    nodes.append({"name": NODE3_NAME, "online": node3_up, "clients": "---", "rx": "---", "tx": "---"})

    return {
        "nodes": nodes,
        "totalClients": total_clients if api_success else "---",
        "overallStatus": "Everything looks good" if (api_success or any(n["online"] for n in nodes)) else "Check Connection"
    }
