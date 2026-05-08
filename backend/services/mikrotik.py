# backend/services/mikrotik.py
import httpx
import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("MIKROTIK_HOST", "")
USER = os.getenv("MIKROTIK_USER", "")
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
    # Always display in Mbps as requested by the user
    return f"{bps / 1000000:.1f} Mbps"

async def get_interface_stats(client, interface_name):
    try:
        # We use a 1-second duration to get a stable average speed 
        # instead of a millisecond-level snapshot.
        resp = await client.post(
            "/interface/monitor-traffic",
            json={"interface": interface_name, "once": True, "duration": "1s"},
            timeout=5.0
        )
        
        print(f"Interface stats response for {interface_name}: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()[0]
            return {
                "rx": format_speed(data.get("rx-bits-per-second", 0)),
                "tx": format_speed(data.get("tx-bits-per-second", 0)),
                "rx_bps": float(data.get("rx-bits-per-second", 0)),
                "tx_bps": float(data.get("tx-bits-per-second", 0))
            }
    except Exception:
        pass
    return {"rx": "0.0 Mbps", "tx": "0.0 Mbps", "rx_bps": 0, "tx_bps": 0}

async def check_internet_reachability(client, interface_name, routing_table=None):
    try:
        params = {
            "address": "8.8.8.8",
            "count": 2,
            "interval": "500ms",
            "interface": interface_name
        }

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
                        # "12ms713us" -> "12"
                        avg_rtt = int(rtt_str.split("ms")[0])
                    break
            return success, avg_rtt
        print(f"Ping request failed for {interface_name} with status code: {resp.status_code}")
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

        def determine_status(label, interface_name, has_internet, rx_bps, tx_bps, latency):
            now = datetime.now()
            if label not in status_cache:
                status_cache[label] = {"status": "NO INTERNET", "pending_status": None, "pending_since": None, "status_changed_at": now}
            
            cached = status_cache[label]
            
            is_disabled = str(interfaces.get(interface_name, {}).get("disabled")).lower() == "true"
            if is_disabled:
                if cached["status"] != "OFFLINE":
                    print(f"[{now.strftime('%H:%M:%S')}] {label.upper()}: Manually Disabled -> OFFLINE")
                    cached["status"] = "OFFLINE"
                    cached["status_changed_at"] = now
                return cached["status"]
            
            # 1. Determine Instantaneous Reading
            if has_internet or rx_bps > 5000000: # 5 Mbps threshold
                current_reading = "ONLINE"
            elif latency == 0 and rx_bps == 0 and tx_bps == 0:
                current_reading = "OFFLINE"
            else:
                current_reading = "NO INTERNET"
                
            # 2. Apply 30-Second Debounce Logic
            if current_reading == cached["status"]:
                # Reading matches status, we are stable. Reset any pending changes.
                cached["pending_status"] = None
                cached["pending_since"] = None
            else:
                if cached.get("pending_status") == current_reading:
                    # We are waiting for this new reading to mature
                    pending_since = cached.get("pending_since", now)
                    if (now - pending_since) >= timedelta(seconds=30):
                        # 30 seconds have passed! Apply the new status.
                        print(f"[{now.strftime('%H:%M:%S')}] {label.upper()}: Status verified -> {current_reading}")
                        cached["status"] = current_reading
                        cached["status_changed_at"] = now
                        cached["pending_status"] = None
                        cached["pending_since"] = None
                else:
                    # A new divergent reading has appeared, start the 30s timer
                    cached["pending_status"] = current_reading
                    cached["pending_since"] = now
                    
            return cached["status"]

        stat1_status = determine_status(WAN1_LABEL, WAN1_NAME, has_internet1, stats1["rx_bps"], stats1["tx_bps"], lat1)
        stat2_status = determine_status(WAN2_LABEL, WAN2_NAME, has_internet2, stats2["rx_bps"], stats2["tx_bps"], lat2)

        return {
            WAN1_LABEL.lower(): {
                "status": stat1_status,
                "statusChangedAt": status_cache[WAN1_LABEL]["status_changed_at"].isoformat() + "Z",
                "latencyMs": lat1,
                "rx": stats1["rx"],
                "tx": stats1["tx"]
            },
            WAN2_LABEL.lower(): {
                "status": stat2_status,
                "statusChangedAt": status_cache[WAN2_LABEL]["status_changed_at"].isoformat() + "Z",
                "latencyMs": lat2,
                "rx": stats2["rx"],
                "tx": stats2["tx"]
            }
        }
