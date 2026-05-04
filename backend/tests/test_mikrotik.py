# backend/tests/test_mikrotik.py
import pytest
import sys
import os

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.mikrotik import get_isp_status

@pytest.mark.asyncio
async def test_get_isp_status():
    status = await get_isp_status()
    # Should have at least two ISP entries (keys are based on labels in .env)
    assert len(status) >= 2
    for isp_name, isp_data in status.items():
        assert "status" in isp_data
        assert "latencyMs" in isp_data
        assert "rx" in isp_data
        assert "tx" in isp_data
