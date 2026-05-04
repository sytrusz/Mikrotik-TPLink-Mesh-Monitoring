# backend/services/deco.py
import asyncio
import os
import subprocess
from tplink_deco_api import DecoClient
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
        if os.name == 'nt':
            args = ['ping', '-n', '1', '-w', '1000', ip]
            kwargs = {'creationflags': getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)}
        else:
            args = ['ping', '-c', '1', '-W', '1', ip]
            kwargs = {}
            
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            **kwargs
        )
        return result.returncode == 0
    except Exception:
        return False

async def ping(ip):
    return await asyncio.to_thread(sync_ping, ip)

def format_speed_kbps(kbps):
    kbps = float(kbps)
    if kbps >= 1000:
        return f"{kbps / 1000:.1f} Mbps"
    else:
        return f"{int(kbps)} kbps"

def sync_get_deco_status():
    try:
        import time
        with DecoClient(DECO_HOST, "admin", DECO_PASS) as deco:
            nodes_data = []
            total_clients = 0
            
            devices = deco.get_device_list()
            for dev in devices:
                mac_hyphen = dev.mac.replace(":", "-")
                try:
                    clients = deco.get_client_list(deco_mac=mac_hyphen)
                    client_count = len(clients)
                    total_clients += client_count
                    
                    up_kbps = sum(c.up_speed for c in clients)
                    down_kbps = sum(c.down_speed for c in clients)
                    
                    rx = format_speed_kbps(down_kbps)
                    tx = format_speed_kbps(up_kbps)
                except Exception as e:
                    print(f"Deco API Error getting clients for {dev.nickname}: {e}")
                    client_count = "---"
                    rx = "---"
                    tx = "---"
                
                nodes_data.append({
                    "name": dev.nickname,
                    "online": dev.inet_status == "online" or dev.group_status == "connected",
                    "clients": client_count,
                    "rx": rx,
                    "tx": tx
                })
                
                # Sleep briefly to avoid triggering error_code=-1 (rate limiting)
                time.sleep(1.0)
                
            return nodes_data, total_clients
    except Exception as e:
        print(f"Deco API Error: {type(e).__name__}: {str(e)}")
        return None, 0

async def get_mesh_status():
    nodes = []
    total_clients = 0
    api_success = False
    
    if DECO_PASS:
        result = await asyncio.to_thread(sync_get_deco_status)
        if result[0] is not None:
            nodes, total_clients = result
            api_success = True
            
        print(f"API access {'succeeded' if api_success else 'failed'} for Deco. Total clients: {total_clients if api_success else 'N/A'}")

    if not api_success:
        is_up = await ping(DECO_HOST)
        nodes.append({
            "name": NODE1_NAME,
            "online": is_up,
            "clients": "---",
            "rx": "---",
            "tx": "---"
        })
        
        print(f"API access failed, fallback to ping. Deco online: {is_up}")

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
