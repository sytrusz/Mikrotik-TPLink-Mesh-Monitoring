import asyncio
from services.deco import get_mesh_status

async def main():
    print("Testing Updated get_mesh_status...")
    status = await get_mesh_status()
    import json
    print(json.dumps(status, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
