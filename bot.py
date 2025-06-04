import discord
from discord.ext import commands
from discord import app_commands
import os
from riot_api import get_valo_rank

TOKEN = os.environ.get("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

MAIN_RANKS = [
    "Iron", "Bronze", "Silver", "Gold",
    "Platinum", "Diamond", "Ascendant", "Immortal", "Radiant"
]

EMOJI_RANKS = {
    "Iron": "⚫", "Bronze": "🟤", "Silver": "⚪", "Gold": "🟡",
    "Platinum": "🔵", "Diamond": "💎", "Ascendant": "💚",
    "Immortal": "❤️", "Radiant": "🌟"
}

RANK_LOGOS = {
    "Iron":     "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/1/largeicon.png",
    "Bronze":   "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/4/largeicon.png",
    "Silver":   "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/7/largeicon.png",
    "Gold":     "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/10/largeicon.png",
    "Platinum": "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/13/largeicon.png",
    "Diamond":  "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/16/largeicon.png",
    "Ascendant":"https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/19/largeicon.png",
    "Immortal": "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/22/largeicon.png",
    "Radiant":  "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/25/largeicon.png"
}

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    await tree.sync()

@tree.command(name="link", description="Lie ton Riot ID (ex: Skye#EUW)")
async def link(interaction: discord.Interaction, riot_id: str):
    await interaction.response.defer()
    rank_name, tier_id = await get_valo_rank(riot_id)
    if not rank_name:
        await interaction.followup.send("Impossible de trouver ton rang. Vérifie ton Riot ID.")
        return

    await assign_main_rank_role(interaction.user, rank_name)

    # Trouve le main rank
    main_rank = next((r for r in MAIN_RANKS if r in rank_name), None)
    emoji = EMOJI_RANKS.get(main_rank, "")
    logo_url = RANK_LOGOS.get(main_rank, "")

    embed = discord.Embed(
        title="🎉 Félicitations !",
        description=f"**Riot ID :** `{riot_id}`\n**Rang Valorant :** {emoji} **{rank_name}**",
        color=0xFFD700
    )
    if logo_url:
        embed.set_thumbnail(url=logo_url)
    embed.set_footer(text="Propulsé par Valorant")

    await interaction.followup.send(
        "Ton rang a bien été enregistré et tu as reçu ton rôle personnalisé !",
        embed=embed
    )

async def assign_main_rank_role(member: discord.Member, full_rank: str):
    guild = member.guild
    main_rank = next((r for r in MAIN_RANKS if r in full_rank), None)
    if not main_rank:
        return

    emoji = EMOJI_RANKS.get(main_rank, "")
    role_name = f"{emoji} {main_rank}"

    roles_to_remove = [role for role in member.roles if any(r in role.name for r in MAIN_RANKS)]
    if roles_to_remove:
        await member.remove_roles(*roles_to_remove)

    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        role = await guild.create_role(name=role_name, mentionable=False)

    await member.add_roles(role)

@tree.command(name="rank", description="Affiche le rang Valorant d'un joueur (Pseudo#Tag)")
async def rank(interaction: discord.Interaction, riot_id: str):
    await interaction.response.defer()
    rank_name, tier_id = await get_valo_rank(riot_id)
    if not rank_name:
        await interaction.followup.send("Impossible de trouver ce rang. Vérifie le Riot ID.")
        return

    main_rank = next((r for r in MAIN_RANKS if r in rank_name), None)
    emoji = EMOJI_RANKS.get(main_rank, "")
    logo_url = RANK_LOGOS.get(main_rank, "")

    embed = discord.Embed(
        title="Rang Valorant",
        description=f"**Riot ID :** `{riot_id}`\n**Rang :** {emoji} **{rank_name}**",
        color=0x3498db
    )
    if logo_url:
        embed.set_thumbnail(url=logo_url)
    embed.set_footer(text="Propulsé par Valorant")

    await interaction.followup.send(embed=embed)

bot.run(TOKEN)
