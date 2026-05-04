# backend/tests/test_deco.py
import pytest
import sys
import os

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.deco import get_mesh_status

@pytest.mark.asyncio
async def test_get_mesh_status():
    status = await get_mesh_status()
    assert isinstance(status["nodes"], list)
    assert len(status["nodes"]) == 3
    assert "name" in status["nodes"][0]
    assert "online" in status["nodes"][0]
    assert "totalClients" in status
    assert "overallStatus" in status
