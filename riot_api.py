import aiohttp
import os

async def get_valo_rank(riot_id: str):
    try:
        name, tag = riot_id.split("#")
    except ValueError:
        print("Format Riot ID incorrect :", riot_id)
        return None, None

    url = f"https://api.henrikdev.xyz/valorant/v1/mmr/eu/{name}/{tag}"
    API_KEY = os.environ.get("HENRIK_API_KEY")
    # DO NOT add Bearer/Basic
    headers = {
        "Authorization": API_KEY
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            print("URL appelée :", url)
            print("Status code :", resp.status)
            data = await resp.json()
            print("Réponse API :", data)
            if resp.status != 200 or data.get("status", 0) != 200 or not data.get("data"):
                return None, None
            return data["data"]["currenttierpatched"], data["data"]["currenttier"]

