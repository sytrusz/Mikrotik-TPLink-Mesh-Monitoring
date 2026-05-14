# Deployment & Maintenance Guide

This document details the complete deployment lifecycle for the MikroTik & TP-Link Mesh Monitoring dashboard. It covers building the frontend, setting up the backend as a background service on a Debian server, configuring the Telegram Bot, and establishing a local domain name.

---

## 1. Frontend Setup & Deployment (Static Export)

Because the dashboard runs on a low-power Debian server, we use Next.js **Static HTML Export**. This removes the need for a Node.js server and dramatically improves performance.

### A. Build on Development PC
You must compile the code on your main development computer (e.g., Fedora laptop):
```bash
cd frontend
# Ensure next.config.ts has output: 'export'
npm run build
```
This generates an `out/` directory containing pure HTML, CSS, and JS.

### B. Transfer to Server
Securely copy the generated `out/` directory to the Debian server's home folder:
```bash
scp -r ./out <your-username>@<debian-server-ip>:/home/<your-username>/
```

### C. Host as a Background Service (Debian Server)
We use Python's built-in HTTP server to serve these static files on **Port 80**, allowing access without typing `:3000`.

1. Create the systemd service file:
   `sudo nano /etc/systemd/system/frontend-server.service`
2. Paste the following configuration:
   ```ini
   [Unit]
   Description=Static Frontend Server
   After=network.target

   [Service]
   # Runs as root to bind to restricted Port 80
   User=root
   WorkingDirectory=/home/<your-username>
   ExecStart=/usr/bin/python3 -m http.server 80 --directory out
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```
3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable frontend-server
   sudo systemctl start frontend-server
   ```

---

## 2. Backend Setup & Deployment (FastAPI)

The backend handles the hardware polling, the status debouncer, and the Telegram bot. 

### A. Environment Preparation
On the Debian server, ensure your project is up to date and your `.env` file exists:
```bash
cd ~/Mikrotik-TPLink-Mesh-Monitoring/backend
# Pull latest code
git pull origin <branch-name>

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Ensure your .env file is present with your credentials:
# MIKROTIK_HOST, MIKROTIK_USER, MIKROTIK_PASS
# TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
```

### B. Host as a Background Service
To keep the backend running 24/7 independently of terminal sessions:

1. Create the systemd service file:
   `sudo nano /etc/systemd/system/network-monitor.service`
2. Paste the following configuration:
   ```ini
   [Unit]
   Description=Mikrotik Mesh Monitoring Backend
   After=network.target

   [Service]
   User=<your-username>
   WorkingDirectory=/home/<your-username>/Mikrotik-TPLink-Mesh-Monitoring/backend
   ExecStart=/home/<your-username>/Mikrotik-TPLink-Mesh-Monitoring/backend/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable network-monitor
   sudo systemctl start network-monitor
   ```

### C. Useful Management Commands
- **Check Status:** `sudo systemctl status network-monitor`
- **View Live Logs:** `journalctl -u network-monitor -f`
- **Apply Code Updates:** After running `git pull`, run `sudo systemctl restart network-monitor`

---

## 3. Local Domain Setup (`<your-domain.local>`)

To access the dashboard using `http://<your-domain.local>` instead of an IP address, add a Static DNS record to your MikroTik router. Because the frontend runs on Port 80, no port forwarding is required.

**Via WinBox/WebFig:**
1. Go to **IP** -> **DNS** -> **Static**.
2. Add a new entry:
   - **Name:** `<your-domain.local>`
   - **Address:** `<your-debian-server-ip>` (The Debian server's IP)
3. Click **OK**.

**Via MikroTik Terminal:**
```bash
/ip dns static add name=<your-domain.local> address=<your-debian-server-ip>
```

---

## 4. Telegram Chat-Ops Bot Configuration

The system provides two-way interaction through Telegram, allowing you to check status and auto-recover disabled ports.

### Enabling the Menu Shortcuts
To add the blue "Menu" button with quick-access commands to your bot's chat interface:
1. Open a chat with **@BotFather** in Telegram.
2. Send `/mybots`, select your monitoring bot, and tap **Edit Bot** -> **Edit Commands**.
3. Send this exact text:
   ```text
   status - Check network status and health
   logs - Show recent outage history
   mesh - Show Deco mesh node status
   ```

### Supported Commands
- `/status` : Returns a live snapshot of ISPs, latency, and router health.
- `/logs` : Displays the recent outage history table directly in chat.
- `/mesh` : Returns current mesh node status and client counts.

### Auto-Recovery Protocol
If the backend debouncer verifies an ISP has dropped, the bot sends an alert with an inline button: **[ ✅ Re-enable <ISP> ]**. Tapping this safely re-enables the interface via the MikroTik API after you have physically verified the connection.
