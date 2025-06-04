import discord
from discord.ext import commands
from discord import app_commands
import json
from riot_api import get_valo_rank

with open("config.json") as f:
    CONFIG = json.load(f)

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

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    await tree.sync()

@tree.command(name="link", description="Lie ton Riot ID (ex: Skye#EUW)")
async def link(interaction: discord.Interaction, riot_id: str):
    await interaction.response.defer()
    rank = await get_valo_rank(riot_id)
    if not rank:
        await interaction.followup.send("Impossible de trouver ton rang. Vérifie ton Riot ID.")
        return

    await assign_main_rank_role(interaction.user, rank)
    await interaction.followup.send(f"Ton rang est : **{rank}** !")

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
    rank = await get_valo_rank(riot_id)
    if not rank:
        await interaction.followup.send("Impossible de trouver ce rang. Vérifie le Riot ID.")
        return
    await interaction.followup.send(f"Le rang de **{riot_id}** est : **{rank}** !")

bot.run(CONFIG["TOKEN"])
