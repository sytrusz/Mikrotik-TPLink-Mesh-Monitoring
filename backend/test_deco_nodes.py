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
            nodes = deco.get_device_list()
            print("Trying hyphenated MAC...")
            n = nodes[0]
            mac_hyphen = n.mac.replace(":", "-")
            try:
                clients = deco.get_client_list(deco_mac=mac_hyphen)
                print(f"Success with {mac_hyphen}! Count: {len(clients)}")
            except Exception as e:
                print(f"Failed with {mac_hyphen}: {e}")
                
            print("Trying overall client list...")
            try:
                clients = deco.get_client_list()
                print(f"Overall count: {len(clients)}")
                # Print full raw dictionary if we can hack into the library's parse_response
                # Since ClientDevice.from_api filters fields, maybe there's an unfiltered field.
                raw = deco.request("admin/client", "client_list", {"operation": "read", "params": {"device_mac": "default"}})
                print("Raw first client:")
                if "client_list" in raw and raw["client_list"]:
                    print(raw["client_list"][0])
            except Exception as e:
                print(f"Failed overall: {e}")

    except Exception as e:
        print(f"Error: {e}")

test()
