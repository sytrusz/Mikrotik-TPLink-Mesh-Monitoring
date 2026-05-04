# Network Status Dashboard Implementation Plan (FastAPI + Next.js)

**Goal:** Build a local website hosted on the network to display the status, speed, and latency of 2 ISP networks connected to a MikroTik router and the connection status of the Mesh Wi-Fi nodes.

**Architecture:** A FastAPI (Python) backend queries the MikroTik router via REST API and pings Mesh nodes for status. The backend exposes a unified JSON API. A Next.js (TypeScript) frontend consumes this API to display a responsive dashboard.

**Tech Stack:** Python, FastAPI, Next.js, React, Tailwind CSS.

---

### Task 1: Backend Initialization
- Setup FastAPI and CORS.
- Implement `/api/status` endpoint.

### Task 2: MikroTik Service
- Implement interface status and traffic monitoring.
- Implement internet reachability checks via ping through specific routing tables.

### Task 3: Mesh Service
- Implement mesh node status via ICMP ping.
- Attempt client count retrieval via unofficial API libraries.

### Task 4: API Integration
- Aggregate data from both services into a single JSON response with timestamps.

### Task 5: Frontend Dashboard
- Build a responsive UI with 3-state status indicators (Online, No Internet, Offline).
- Implement 5-second automatic data polling.

### Task 6: Configuration
- Move all sensitive hardware details (IPs, credentials, interface names) to environment variables.
