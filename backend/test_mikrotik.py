import asyncio
from services.mikrotik import get_isp_status

async def main():
    print("Testing MikroTik Status...")
    status = await get_isp_status()
    import json
    print(json.dumps(status, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
