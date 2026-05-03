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
