import json

def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)

config = load_config()
BASE_URL = config.get("base_url")
TOKEN = config["discord_token"]
ENDPOINT = config["koboldapp_endpoint"]
COMFY_SERVER_ADDRESS = config["comfy_server_address"]