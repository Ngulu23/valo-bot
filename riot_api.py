import aiohttp
import json

with open("config.json") as f:
    CONFIG = json.load(f)

API_KEY = CONFIG["HENRIK_API_KEY"]

async def get_valo_rank(riot_id: str):
    try:
        name, tag = riot_id.split("#")
    except ValueError:
        return None

    url = f"https://api.henrikdev.xyz/valorant/v1/mmr/eu/{name}/{tag}"
    headers = {"Authorization": API_KEY}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            if data["status"] != 200 or not data.get("data"):
                return None
            return data["data"]["currenttierpatched"]

