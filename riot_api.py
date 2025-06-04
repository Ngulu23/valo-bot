import aiohttp
import os

async def get_valo_rank(riot_id: str):
    try:
        name, tag = riot_id.split("#")
    except ValueError:
        print("Format Riot ID incorrect :", riot_id)
        return None, None

    url = f"https://api.henrikdev.xyz/valorant/v1/mmr/eu/{name}/{tag}"
    API_KEY = os.environ.get("HENRIK_API_KEY")  # Doit être ajouté dans tes variables d'environnement

    headers = {"Authorization": API_KEY} if API_KEY else {}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            if resp.status != 200 or data.get("status", 0) != 200 or not data.get("data"):
                print("Erreur API:", data)
                return None, None
            return data["data"]["currenttierpatched"], data["data"]["currenttier"]

