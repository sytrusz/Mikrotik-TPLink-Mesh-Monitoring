# Network Status Dashboard Implementation Plan (FastAPI + Next.js)

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a local website hosted on the network to display the status, speed, and latency of 2 ISP networks connected to a MikroTik router and the connection status of the Deco Mesh Wi-Fi nodes.

**Architecture:** A FastAPI (Python) backend will query the MikroTik router via its REST API (for ISP link status, tx/rx, and latency pings) and use networking libraries/scripts to query the Deco Mesh (via ICMP or unofficial libraries) for node status. The backend will expose a unified JSON API. A Next.js (TypeScript) frontend will consume this API to display a responsive, modern dashboard.

**Tech Stack:** Python, FastAPI, Pytest (Backend) & Next.js, React, Tailwind CSS, Jest (Frontend).

---

### Task 1: Backend Initialization (FastAPI)

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/tests/test_main.py`

**Step 1: Initialize Python environment & dependencies**

Run: `mkdir backend && cd backend && python -m venv venv && .\venv\Scripts\activate && pip install fastapi uvicorn pytest httpx`
Expected: Virtual environment created and dependencies installed.
*Note: Write the dependencies to `backend/requirements.txt`: `fastapi\nuvicorn\npytest\nhttpx`*

**Step 2: Write the failing test for the root endpoint**

```python
# backend/tests/test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/api/status")
    assert response.status_code == 200
    assert "status" in response.json()
```

**Step 3: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && pytest tests/test_main.py`
Expected: FAIL (ModuleNotFoundError: No module named 'main')

**Step 4: Write minimal FastAPI implementation**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
def read_status():
    return {"status": "ok"}
```

**Step 5: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && pytest tests/test_main.py`
Expected: PASS

**Step 6: Commit**

```bash
git init
echo "backend/venv/\nbackend/__pycache__/\nnode_modules/\n.env" > .gitignore
git add backend/requirements.txt backend/main.py backend/tests/test_main.py .gitignore
git commit -m "chore: initialize fastapi backend"
```

### Task 2: Implement MikroTik API Integration (Mocked in Python)

*Note: Since the agent does not have direct access to the physical router in this planning phase, we build a service that fetches data, with a mock for tests.*

**Files:**
- Create: `backend/services/mikrotik.py`
- Create: `backend/tests/test_mikrotik.py`

**Step 1: Write the failing test for fetching ISP status**

```python
# backend/tests/test_mikrotik.py
import pytest
from services.mikrotik import get_isp_status

@pytest.mark.asyncio
async def test_get_isp_status():
    status = await get_isp_status()
    assert "converge" in status
    assert "pldt" in status
    assert status["converge"]["up"] is True
```

**Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && pytest tests/test_mikrotik.py`
Expected: FAIL (pytest-asyncio missing or ModuleNotFoundError)
*Note: Ensure `pytest-asyncio` is added to requirements.txt and installed.*

**Step 3: Write minimal implementation**

```python
# backend/services/mikrotik.py
import asyncio

async def get_isp_status():
    # In a real scenario, this will use httpx to call RouterOS REST API.
    # For now, we mock the expected structure based on the provided requirements.
    await asyncio.sleep(0.1) # Simulate network delay
    return {
        "converge": { "up": True, "latencyMs": 15, "rx": "13.6 Mbps", "tx": "405.8 kbps" },
        "pldt": { "up": True, "latencyMs": 25, "rx": "5.0 Mbps", "tx": "1872.7 kbps" }
    }
```

**Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && pip install pytest-asyncio && pytest tests/test_mikrotik.py`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/services/mikrotik.py backend/tests/test_mikrotik.py backend/requirements.txt
git commit -m "feat: implement mikrotik service with mocked ISP data"
```

### Task 3: Implement Deco Mesh Integration (Mocked in Python)

**Files:**
- Create: `backend/services/deco.py`
- Create: `backend/tests/test_deco.py`

**Step 1: Write the failing test for fetching Mesh status**

```python
# backend/tests/test_deco.py
import pytest
from services.deco import get_mesh_status

@pytest.mark.asyncio
async def test_get_mesh_status():
    status = await get_mesh_status()
    assert isinstance(status["nodes"], list)
    assert len(status["nodes"]) > 0
    assert "name" in status["nodes"][0]
    assert "online" in status["nodes"][0]
```

**Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && pytest tests/test_deco.py`
Expected: FAIL (ModuleNotFoundError)

**Step 3: Write minimal implementation**

```python
# backend/services/deco.py
import asyncio

async def get_mesh_status():
    # Mocking Deco status based on provided screenshots
    await asyncio.sleep(0.1)
    return {
        "nodes": [
            { "name": "Main - 2F", "online": True, "clients": 11, "rx": "8.8 Mbps", "tx": "263 kbps" },
            { "name": "Elma", "online": True, "clients": 1, "rx": "71 kbps", "tx": "37 kbps" },
            { "name": "Living Room - 1F", "online": True, "clients": 2, "rx": "49 kbps", "tx": "36 kbps" }
        ],
        "totalClients": 14,
        "overallStatus": "Everything looks good"
    }
```

**Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && pytest tests/test_deco.py`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/services/deco.py backend/tests/test_deco.py
git commit -m "feat: implement deco mesh service mock"
```

### Task 4: Integrate Backend Services into API Endpoint

**Files:**
- Modify: `backend/main.py`
- Modify: `backend/tests/test_main.py`

**Step 1: Update API test to expect aggregated network data**

Modify `backend/tests/test_main.py`:

```python
# backend/tests/test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "isps" in data
    assert "mesh" in data
    assert "timestamp" in data
```

**Step 2: Run test to verify it fails**

Run: `cd backend && .\venv\Scripts\activate && pytest tests/test_main.py`
Expected: FAIL (AssertionError: assert 'isps' in {'status': 'ok'})

**Step 3: Write minimal implementation in main.py**

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from services.mikrotik import get_isp_status
from services.deco import get_mesh_status

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/status")
async def read_status():
    isps = await get_isp_status()
    mesh = await get_mesh_status()
    return {
        "isps": isps,
        "mesh": mesh,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
```

**Step 4: Run test to verify it passes**

Run: `cd backend && .\venv\Scripts\activate && pytest tests/test_main.py`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/main.py backend/tests/test_main.py
git commit -m "feat: aggregate mikrotik and deco data in api endpoint"
```

### Task 5: Frontend Initialization (Next.js)

**Files:**
- Create: `frontend/` (via create-next-app)

**Step 1: Initialize Next.js project**

Run: `npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm`
Expected: Next.js project created in `frontend/` directory.

**Step 2: Commit**

```bash
git add frontend/
git commit -m "chore: initialize next.js frontend"
```

### Task 6: Build Frontend Dashboard UI

**Files:**
- Modify: `frontend/src/app/page.tsx`
- Modify: `frontend/src/app/globals.css` (if needed for extra styling)

**Step 1: Create the Dashboard Component**

Replace the contents of `frontend/src/app/page.tsx` with a component that fetches from the backend (assuming backend runs on port 8000).

```tsx
// frontend/src/app/page.tsx
'use client';

import { useEffect, useState } from 'react';

export default function Home() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/status');
      if (!res.ok) throw new Error('Failed to fetch');
      const json = await res.json();
      setData(json);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (error) return <div className="p-8 text-red-500">Error: {error}</div>;
  if (!data) return <div className="p-8">Loading...</div>;

  return (
    <main className="min-h-screen bg-gray-900 text-gray-100 p-8 font-sans">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-10">
          <h1 className="text-4xl font-bold mb-2">Network Status</h1>
          <p className="text-gray-400">Last updated: {new Date(data.timestamp).toLocaleTimeString()}</p>
        </header>

        <section className="mb-10">
          <h2 className="text-2xl font-semibold mb-4 border-b border-gray-700 pb-2">Internet Connections</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(data.isps).map(([name, isp]: [string, any]) => (
              <div key={name} className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                <h3 className="text-xl font-medium uppercase mb-2">{name}</h3>
                <p className={`font-bold ${isp.up ? 'text-green-500' : 'text-red-500'}`}>
                  {isp.up ? 'ONLINE' : 'OFFLINE'}
                </p>
                <div className="mt-4 text-sm text-gray-400 space-y-1">
                  <p>Latency: {isp.latencyMs} ms</p>
                  <p>↓ {isp.rx} | ↑ {isp.tx}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-4 border-b border-gray-700 pb-2">Mesh Network (Deco)</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {data.mesh.nodes.map((node: any) => (
              <div key={node.name} className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                <h3 className="text-lg font-medium mb-2">{node.name}</h3>
                <p className={`font-bold ${node.online ? 'text-green-500' : 'text-red-500'}`}>
                  {node.online ? 'ONLINE' : 'OFFLINE'}
                </p>
                <div className="mt-4 text-sm text-gray-400 space-y-1">
                  <p>Clients: {node.clients}</p>
                  <p>↓ {node.rx} | ↑ {node.tx}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
```

**Step 2: Commit**

```bash
git add frontend/src/app/page.tsx
git commit -m "feat: add next.js dashboard ui fetching from fastapi"
```

### Task 7: Explore Real Data Retrieval (Manual Task)

To move past mock data:
1.  **MikroTik:** Configure RouterOS API on the hex. Ensure the Python backend can authenticate using `httpx` to the `/rest` endpoints. Query `/rest/interface` and `/rest/interface/monitor-traffic`.
2.  **Deco Mesh:** Investigate Python libraries like `tplink-deco-api` or network scraping techniques to replace the mocked Deco service. 

*This task doesn't have a code snippet as it requires empirical testing against the physical network.*
