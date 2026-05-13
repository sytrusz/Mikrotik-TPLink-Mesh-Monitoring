# Mikrotik-TPLink-Mesh-Monitoring 📡

A real-time, sleek monitoring dashboard specialized for **MikroTik routers** and **TP-Link Deco Mesh** systems with Dual-ISP failover. 

This project solves the "True-Negative" problem where a router interface shows "Connected" even when the internet is experiencing a brownout or service failure, while providing an aesthetic, real-time interface for local network monitoring.

![Status](https://img.shields.io/badge/Status-Ongoing-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Key Features

### 📡 Real-time Monitoring
*   **Dual-ISP Monitoring:** Real-time tracking of two independent WAN connections with live throughput and latency metrics.
*   **True-Negative Detection:** Advanced logic that combines ICMP pings via specific interfaces and real-time interface throughput to verify actual internet reachability, protecting against false offline/online flickering.
*   **Debounced Status Machine:** A robust 30-second verification window that eliminates false alarms from modem noise, fake pings, and transient traffic spikes.
*   **Mesh Network Visibility:** Detailed status monitoring for TP-Link Deco Mesh nodes, including active client counts and aggregate speeds per node.
*   **Router Health:** Live display of MikroTik CPU load, RAM usage, temperature, and system uptime.
*   **Smart API Caching:** Built-in server-side background polling that maintains constant, warm sessions with hardware for 0ms response times on the frontend.

### 🤖 Chat-Ops & Alerts
*   **Telegram Bot Integration:**
    *   **Push Notifications:** Real-time alerts when an ISP officially drops or recovers.
    *   **Interactive Controls:** Alerts include inline buttons to manually re-enable interfaces (via MikroTik API) if they have been automatically disabled.
    *   **Command Support:** Query the bot with `/status`, `/logs`, or `/mesh` to get current system snapshots directly on your phone.
*   **Outage Logging:** Automatically logs ISP drop and recovery events (with precise timestamps) to `outages.json` for historical tracking.

## 🛠️ Tech Stack & Credits

*   **Backend:** Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), `python-telegram-bot`
*   **Frontend:** [Next.js 14+](https://nextjs.org/) (App Router), React, TypeScript, Tailwind CSS
*   **MikroTik Integration:** Utilizes the official [MikroTik RouterOS v7 REST API](https://help.mikrotik.com/docs/display/ROS/REST+API).
*   **Deco Integration:** Powered by the brilliant open-source library [ha-tplink-deco](https://github.com/amosyuen/ha-tplink-deco) by amosyuen, allowing me to fetch granular mesh network data.

## 📋 Prerequisites

*   **MikroTik:** RouterOS v7.x with `www` or `www-ssl` service enabled.
*   **Deco:** TP-Link Deco Mesh system with a management password set.
*   **Host:** A local device (Raspberry Pi, NAS, or Mini PC) to host the services.

## 🚀 Setup Instructions

### 0. Install System Dependencies

#### Debian / Ubuntu
```bash
sudo apt install python3 python3-pip nodejs npm
```

### 1. Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```
*Edit `.env` with your local IP addresses, interface names, passwords, and Telegram credentials.*

Run the backend:
```bash
python -m uvicorn main:app --host 0.0.0.0 --reload
```

### 2. Frontend Setup (Next.js)

Configure your `frontend/next.config.ts` for static export to support low-power devices:
```typescript
const nextConfig: NextConfig = {
  output: 'export',
};
```

Build the frontend:
```bash
cd frontend
npm install
npm run build
npm run start
```
*(Serve the generated `out/` folder using Nginx or Python's `http.server`.)*

## ⚙️ Configuration (.env)

| Variable | Description |
| :--- | :--- |
| `MIKROTIK_HOST` | Local IP of your MikroTik router |
| `MIKROTIK_USER` | WinBox/API Username |
| `MIKROTIK_PASS` | WinBox/API Password |
| `DECO_HOST` | Local IP of the Main Deco unit |
| `DECO_PASS` | Your TP-Link Owner Password |
| `TELEGRAM_BOT_TOKEN` | Your Telegram Bot Token from BotFather |
| `TELEGRAM_CHAT_ID` | Your numeric Telegram Chat ID |

## 🗺️ Roadmap
- [x] Backend FastAPI Scaffold
- [x] MikroTik RouterOS v7 REST Integration
- [x] True-Negative internet detection logic
- [x] Next.js Dashboard UI (Modern Dark Theme)
- [x] Deco Mesh API (per-node client routing & caching)
- [x] Push Notifications (Telegram)
- [x] Automated Failover Trigger (MikroTik Interface Disabler)
- [ ] **Daily Automated Speed Tests**
  - Integrate a speed test tool (like `speedtest-cli`) to run automatically at off-peak hours (e.g., 3:00 AM) on both ISPs.
  - Display the last known true capability of the ISP on the dashboard, to compare against the live bandwidth usage.

- [ ] **Automated Failover Trigger with Manual Recovery Button**
  - **Problem:** Native MikroTik load-balancing sometimes fails to drop a connection experiencing heavy-load failures.
  - **Automated Action:** When the backend debouncer officially registers 'NO INTERNET' or 'OFFLINE' for an ISP, trigger a POST request to the MikroTik REST API to actively `disable` that specific interface.
  - **Interactive Recovery:** The Telegram alert will include an **Inline Button** (e.g., "[ ✅ Re-enable Converge ]"). Tapping this button will send a command back to the server to re-enable the port after the user has finished their physical verification.

## 📄 License
This project is licensed under the MIT License.