# backend/services/mikrotik.py
import httpx
import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("MIKROTIK_HOST", "192.168.30.1")
USER = os.getenv("MIKROTIK_USER", "admin")
PASS = os.getenv("MIKROTIK_PASS", "")
SSL = os.getenv("MIKROTIK_USE_SSL", "false").lower() == "true"

WAN1_NAME = os.getenv("MIKROTIK_WAN1_NAME", "ether1")
WAN1_LABEL = os.getenv("MIKROTIK_WAN1_LABEL", "ISP 1")
WAN1_TABLE = os.getenv("MIKROTIK_WAN1_TABLE", "")

WAN2_NAME = os.getenv("MIKROTIK_WAN2_NAME", "ether2")
WAN2_LABEL = os.getenv("MIKROTIK_WAN2_LABEL", "ISP 2")
WAN2_TABLE = os.getenv("MIKROTIK_WAN2_TABLE", "")

BASE_URL = f"{'https' if SSL else 'http'}://{HOST}/rest"

# Cache for "Status Persistence" to prevent flickering
# format: {isp_label: {"status": str, "last_check": datetime}}
status_cache = {}

def format_speed(bps):
    bps = float(bps)
    if bps >= 1000000:
        return f"{bps / 1000000:.1f} Mbps"
    elif bps >= 1000:
        return f"{bps / 1000:.1f} kbps"
    else:
        return f"{bps} bps"

async def get_interface_stats(client, interface_name):
    try:
        # We use a 1-second duration to get a stable average speed 
        # instead of a millisecond-level snapshot.
        resp = await client.post(
            "/interface/monitor-traffic",
            json={"interface": interface_name, "once": True, "duration": "1s"},
            timeout=5.0
        )
        if resp.status_code == 200:
            data = resp.json()[0]
            return {
                "rx": format_speed(data.get("rx-bits-per-second", 0)),
                "tx": format_speed(data.get("tx-bits-per-second", 0)),
                "rx_bps": float(data.get("rx-bits-per-second", 0))
            }
    except Exception:
        pass
    return {"rx": "0 bps", "tx": "0 bps", "rx_bps": 0}

async def check_internet_reachability(client, interface_name, routing_table=None):
    try:
        params = {
            "address": "8.8.8.8",
            "count": 2,
            "interval": "500ms"
        }
        if routing_table:
            params["routing-table"] = routing_table
        else:
            params["interface"] = interface_name

        resp = await client.post("/ping", json=params, timeout=5.0)
        
        if resp.status_code == 200:
            results = resp.json()
            # Success if any packet received or RTT calculated
            success = any(
                (int(r.get("received", "0")) > 0) or 
                (r.get("status") == "echo reply") or
                ("avg-rtt" in r)
                for r in results
            )
            
            avg_rtt = 0
            for r in results:
                if "avg-rtt" in r:
                    rtt_str = str(r["avg-rtt"])
                    if "ms" in rtt_str:
                        avg_rtt = int(rtt_str.replace("ms", ""))
                    break
            return success, avg_rtt
    except Exception:
        pass
    return False, 0

async def get_isp_status():
    async with httpx.AsyncClient(base_url=BASE_URL, auth=(USER, PASS), verify=False) as client:
        try:
            resp = await client.get("/interface")
            interfaces = {i["name"]: i for i in resp.json()}
        except Exception:
            interfaces = {}

        # Parallelize all network checks
        stats_tasks = [
            get_interface_stats(client, WAN1_NAME),
            get_interface_stats(client, WAN2_NAME)
        ]
        reach_tasks = [
            check_internet_reachability(client, WAN1_NAME, routing_table=WAN1_TABLE),
            check_internet_reachability(client, WAN2_NAME, routing_table=WAN2_TABLE)
        ]

        results = await asyncio.gather(*(stats_tasks + reach_tasks))
        stats1, stats2, (has_internet1, lat1), (has_internet2, lat2) = results

        def determine_status(label, interface_name, has_internet, rx_bps):
            is_running = str(interfaces.get(interface_name, {}).get("running")).lower() == "true"
            if not is_running:
                return "OFFLINE"
            
            # STABILITY LOGIC:
            # 1. If ping succeeds -> Always ONLINE
            # 2. If ping fails but traffic > 50kbps -> Likely ONLINE (ping was just blocked)
            # 3. We use a 10s 'grace period' where it must fail BOTH for 10s before showing NO INTERNET
            
            current_is_up = has_internet or rx_bps > 50000
            now = datetime.now()
            
            if current_is_up:
                status_cache[label] = {"status": "ONLINE", "last_up": now}
                return "ONLINE"
            
            # If failing, check if it was UP recently (within last 15 seconds)
            last_up = status_cache.get(label, {}).get("last_up")
            if last_up and (now - last_up) < timedelta(seconds=15):
                return "ONLINE" # Suppress flicker

            return "NO INTERNET"

        return {
            WAN1_LABEL.lower(): {
                "status": determine_status(WAN1_LABEL, WAN1_NAME, has_internet1, stats1["rx_bps"]),
                "latencyMs": lat1,
                "rx": stats1["rx"],
                "tx": stats1["tx"]
            },
            WAN2_LABEL.lower(): {
                "status": determine_status(WAN2_LABEL, WAN2_NAME, has_internet2, stats2["rx_bps"]),
                "latencyMs": lat2,
                "rx": stats2["rx"],
                "tx": stats2["tx"]
            }
        }
