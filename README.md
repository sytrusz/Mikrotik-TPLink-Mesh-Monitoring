# Network Status Dashboard (MikroTik + TP-Link Deco) 📡

A real-time monitoring dashboard specialized for **MikroTik routers** and **TP-Link Deco Mesh** systems with Dual-ISP failover. 

This project solves the "True-Negative" problem where a router interface shows "Connected" even when the internet is experiencing a brownout or service failure.

![Status](https://img.shields.io/badge/Status-Ongoing-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Key Features

*   **Dual-ISP Monitoring:** Real-time tracking of two independent WAN connections (e.g., Converge & PLDT).
*   **True-Negative Detection:** Advanced logic that combines ICMP pings via specific routing tables and real-time interface throughput to verify actual internet reachability.
*   **Mesh Network Visibility:** Status monitoring for TP-Link Deco Mesh nodes (Main, Satellite units).
*   **Stability Engine:** 1-second average throughput monitoring and status smoothing to prevent flickering metrics.
*   **Live Dashboard:** Auto-polling dashboard (every 5 seconds) built with a modern dark-mode aesthetic.
*   **Interactive API Docs:** Built-in Swagger UI for exploring the backend endpoints.

## 🛠️ Tech Stack

*   **Backend:** Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
*   **Frontend:** [Next.js 14+](https://nextjs.org/) (App Router), React, TypeScript, Tailwind CSS
*   **Networking:** MikroTik RouterOS v7 REST API, `tplinkrouterc6u` (Unofficial Deco API)

## 📋 Prerequisites

*   **MikroTik:** RouterOS v7.x with `www` or `www-ssl` service enabled.
*   **Deco:** TP-Link Deco Mesh system with a management password set.
*   **Host:** A local device (Raspberry Pi, NAS, or Mini PC) to host the services.

## 🚀 Setup Instructions

### 0. Install System Dependencies

#### Fedora
```bash
sudo dnf install python3 python3-pip nodejs npm
```

#### Arch Linux
```bash
sudo pacman -S python python-pip nodejs npm
```

### 1. Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# or: source venv/bin/activate # Linux/Mac

pip install -r requirements.txt
cp .env.example .env
```
*Edit `.env` with your router IPs and credentials.*

Run the backend:
```bash
python -m uvicorn main:app --reload
```

### 2. Frontend Setup (Next.js)
```bash
cd frontend
npm install
npm run dev
```

Visit the dashboard at: `http://localhost:3000`

## ⚙️ Configuration (.env)

| Variable | Description |
| :--- | :--- |
| `MIKROTIK_HOST` | Local IP of your MikroTik router (e.g., 192.168.30.1) |
| `MIKROTIK_USER` | WinBox/API Username |
| `MIKROTIK_PASS` | WinBox/API Password |
| `MIKROTIK_WAN1_NAME` | Name of first WAN interface (e.g., ether1) |
| `MIKROTIK_WAN1_TABLE` | Routing table for ISP 1 (for forced pings) |
| `DECO_HOST` | Local IP of Main Deco unit (e.g., 192.168.68.1) |
| `NODE2_IP` | Local IP of secondary Mesh node |

## 🗺️ Roadmap (Ongoing)

- [x] Backend FastAPI Scaffold
- [x] MikroTik RouterOS v7 REST Integration
- [x] True-Negative internet detection logic
- [x] Next.js Dashboard UI
- [x] Deco Mesh API & Ping integration
- [ ] Historical Latency Graphs (In-progress)
- [ ] Telegram/Discord Notifications for ISP downtime
- [ ] Docker Compose support for easy deployment

## 📄 License
This project is licensed under the MIT License.
