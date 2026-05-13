import json
import os
from datetime import datetime

OUTAGE_FILE = os.path.join(os.path.dirname(__file__), "..", "outages.json")

def log_status_change(isp_label, old_status, new_status, timestamp=None):
    if not timestamp:
        timestamp = datetime.utcnow().isoformat() + "Z"
    
    # We only care if it drops or recovers
    if old_status == new_status:
        return
        
    try:
        if os.path.exists(OUTAGE_FILE):
            with open(OUTAGE_FILE, "r") as f:
                logs = json.load(f)
        else:
            logs = []
    except Exception:
        logs = []

    # If it is dropping
    if new_status in ["NO INTERNET", "OFFLINE"] and old_status == "ONLINE":
        logs.insert(0, {
            "isp": isp_label,
            "dropped_at": timestamp,
            "recovered_at": None,
            "reason": new_status
        })
    # If it is recovering
    elif new_status == "ONLINE" and old_status in ["NO INTERNET", "OFFLINE"]:
        # Find the most recent unresolved outage for this ISP
        for log in logs:
            if log["isp"] == isp_label and log["recovered_at"] is None:
                log["recovered_at"] = timestamp
                break
        else:
            # If no unresolved outage is found, just log a recovery
            logs.insert(0, {
                "isp": isp_label,
                "dropped_at": None,
                "recovered_at": timestamp,
                "reason": "---"
            })
            
    # Keep only the last 5-10 logs
    logs = logs[:10]

    with open(OUTAGE_FILE, "w") as f:
        json.dump(logs, f, indent=2)

def get_outage_logs():
    try:
        if os.path.exists(OUTAGE_FILE):
            with open(OUTAGE_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return []
