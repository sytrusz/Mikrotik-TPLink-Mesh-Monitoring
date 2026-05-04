# Mikrotik-TPLink-Mesh-Monitoring 📡

A real-time, sleek monitoring dashboard specialized for **MikroTik routers** and **TP-Link Deco Mesh** systems with Dual-ISP failover. 

This project solves the "True-Negative" problem where a router interface shows "Connected" even when the internet is experiencing a brownout or service failure, while providing an aesthetic, real-time interface for local network monitoring.

![Status](https://img.shields.io/badge/Status-Ongoing-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Key Features

*   **Dual-ISP Monitoring:** Real-time tracking of two independent WAN connections with live throughput and latency metrics.
*   **True-Negative Detection:** Advanced logic that combines ICMP pings via specific interfaces and real-time interface throughput to verify actual internet reachability, protecting against false offline/online flickering.
*   **Mesh Network Visibility:** Detailed status monitoring for TP-Link Deco Mesh nodes, including active client counts and aggregate speeds per node.
*   **Smart API Caching:** Built-in 60-second server-side caching for the Deco API to prevent rate-limiting and device exhaustion, while maintaining a smooth 5-second polling rate for the MikroTik data.
*   **Live Dashboard:** Auto-polling dashboard built with a modern, dark-mode, responsive UI.

## 🛠️ Tech Stack & Credits

*   **Backend:** Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
*   **Frontend:** [Next.js 14+](https://nextjs.org/) (App Router), React, TypeScript, Tailwind CSS
*   **MikroTik Integration:** Utilizes the official [MikroTik RouterOS v7 REST API](https://help.mikrotik.com/docs/display/ROS/REST+API).
*   **Deco Integration:** Powered by the brilliant open-source library [ha-tplink-deco](https://github.com/amosyuen/ha-tplink-deco) by amosyuen, allowing me to fetch granular mesh network data.

## 📋 Prerequisites

*   **MikroTik:** RouterOS v7.x with `www` or `www-ssl` service enabled.
*   **Deco:** TP-Link Deco Mesh system (e.g., Deco M5) with a management password set.
*   **Host:** A local device (Raspberry Pi, NAS, or Mini PC) to host the services.

## 🚀 Setup Instructions

### 0. Install System Dependencies

#### Fedora
```bash
sudo dnf install python3 python3-pip nodejs npm
```

#### Debian / Ubuntu
```bash
sudo apt install python3 python3-pip nodejs npm
```

### 1. Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate # Linux/Mac (or .\venv\Scripts\activate on Windows)

pip install -r requirements.txt
cp .env.example .env
```
*Edit `.env` with your local IP addresses, interface names, and passwords.*

Run the backend on your local network:
```bash
# Using 0.0.0.0 allows other devices on your Wi-Fi to access the API
python -m uvicorn main:app --host 0.0.0.0 --reload
```

### 2. Frontend Setup (Next.js)

To customize your dashboard's display name, copy the example environment file and edit it:
```bash
cp .env.example .env.local
```
*(Refer to `frontend/.env.example` for the available variables like `NEXT_PUBLIC_NETWORK_NAME`, `NEXT_PUBLIC_MAX_PLAN_MBPS`, and `NEXT_PUBLIC_BACKEND_URL`)*

Build and run the frontend:
```bash
cd frontend
npm install
npm run build
npm run start
```

Visit the dashboard at: `http://<your-host-ip>:3000` (e.g., `http://192.168.1.100:3000`). The dashboard will dynamically detect its host IP and fetch from the backend accordingly.

## ⚙️ Configuration (.env)

| Variable | Description |
| :--- | :--- |
| `MIKROTIK_HOST` | Local IP of your MikroTik router (e.g., 192.168.30.1) |
| `MIKROTIK_USER` | WinBox/API Username |
| `MIKROTIK_PASS` | WinBox/API Password |
| `MIKROTIK_WAN1_NAME` | Name of first WAN interface (e.g., ether1-Converge) |
| `DECO_HOST` | Local IP of the Main Deco unit (e.g., 192.168.68.1) |
| `DECO_PASS` | Your TP-Link Owner Password |
| `NODE1_NAME` | Display name of Main Deco |

## 🗺️ Roadmap (Ongoing)

- [x] Backend FastAPI Scaffold
- [x] MikroTik RouterOS v7 REST Integration
- [x] True-Negative internet detection logic
- [x] Next.js Dashboard UI (Modern Dark Theme)
- [x] Deco Mesh API (per-node client routing & caching)
- [ ] Docker Compose support for easy deployment

## 📄 License
This project is licensed under the MIT License.