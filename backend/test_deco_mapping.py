import os
import time
from dotenv import load_dotenv
from tplink_deco_api import DecoClient

load_dotenv()
DECO_HOST = os.getenv("DECO_HOST", "192.168.68.1")
DECO_PASS = os.getenv("DECO_PASS")

def test():
    try:
        with DecoClient(DECO_HOST, "admin", DECO_PASS) as deco:
            clients = deco.get_client_list()
            print("\n--- Clients ---")
            for c in clients[:10]:
                print(f"Client {c.name}: access_host={c.access_host}, interface={c.interface}")
                
            print("\n--- Client Attributes ---")
            print(vars(clients[0]))
    except Exception as e:
        print(f"Error: {e}")

test()
