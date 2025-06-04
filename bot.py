import discord
from discord.ext import commands
import os
from riot_api import get_valo_rank

TOKEN = os.environ["TOKEN"]

MAIN_RANKS = [
    "Iron", "Bronze", "Silver", "Gold",
    "Platinum", "Diamond", "Ascendant", "Immortal", "Radiant"
]

EMOJI_RANKS = {
    "Iron": "⚫", "Bronze": "🟤", "Silver": "⚪", "Gold": "🟡",
    "Platinum": "🔵", "Diamond": "💎", "Ascendant": "💚",
    "Immortal": "❤️", "Radiant": "🌟"
}

RANK_IMAGES = {
    "Iron":     "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/1/largeicon.png",
    "Bronze":   "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/4/largeicon.png",
    "Silver":   "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/7/largeicon.png",
    "Gold":     "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/10/largeicon.png",
    "Platinum": "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/13/largeicon.png",
    "Diamond":  "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/16/largeicon.png",
    "Ascendant":"https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/19/largeicon.png",
    "Immortal": "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/22/largeicon.png",
    "Radiant":  "https://media.valorant-api.com/competitivetiers/564d8e28-c226-3180-6285-e48a390db8b1/25/largeicon.png",
}

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

class RiotModal(discord.ui.Modal, title="Lien ton compte Valorant"):
    riot_id = discord.ui.TextInput(
        label="Riot ID (Pseudo#Tag)",
        style=discord.TextStyle.short,
        placeholder="Skye#EUW",
        required=True,
        max_length=32
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        riot_id = str(self.riot_id.value).strip()
        rank, rank_num = await get_valo_rank(riot_id)
        if not rank:
            await interaction.followup.send("Impossible de trouver ton rang. Vérifie ton Riot ID !", ephemeral=True)
            return

        await assign_main_rank_role(interaction.user, rank)

        main_rank = next((r for r in MAIN_RANKS if r in rank), rank.split(" ")[0])
        emoji = EMOJI_RANKS.get(main_rank, "")
        rank_img = RANK_IMAGES.get(main_rank, "")

        embed = discord.Embed(
            title="🎉 Félicitations !",
            description=f"**Riot ID** : `{riot_id}`\n**Rang Valorant** : {emoji} **{rank}**",
            color=discord.Color.gold()
        )
        if rank_img:
            embed.set_thumbnail(url=rank_img)
        embed.set_footer(text="Propulsé par Valorant")
        await interaction.followup.send(
            "Ton rang a bien été enregistré et tu as reçu ton rôle personnalisé !",
            embed=embed, ephemeral=True
        )

class RiotLinkButton(discord.ui.View):
    @discord.ui.button(label="🔗 Lier mon compte Riot", style=discord.ButtonStyle.blurple)
    async def link_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RiotModal())

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

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

@bot.command(name="setup_valorank")
@commands.has_permissions(administrator=True)
async def setup_valorank(ctx):
    view = RiotLinkButton()
    embed = discord.Embed(
        title="Valorant Rank Linker",
        description="Clique sur le bouton ci-dessous pour lier ton Riot ID Valorant à ton profil Discord !",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=view)

bot.run(TOKEN)

