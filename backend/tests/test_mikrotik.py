# backend/tests/test_mikrotik.py
import pytest
from services.mikrotik import get_isp_status

@pytest.mark.asyncio
async def test_get_isp_status():
    status = await get_isp_status()
    assert "converge" in status
    assert "pldt" in status
    assert status["converge"]["up"] is True
