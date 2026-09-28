import os
import asyncio
import discord
from dotenv import load_dotenv

load_dotenv("/home/rudra/discord-server-setup/.env")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "1554105137855729724"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    guild = client.get_guild(GUILD_ID)
    channel = discord.utils.get(guild.text_channels, name="superpower-exchange")
    if channel:
        embed = discord.Embed(
            title="⚡ CHOOSE YOUR SUPERPOWERS // THE ASYMMETRIC SKILL TREE",
            description=(
                "In **THE ONE**, we trade superpowers to compound velocity.\n\n"
                "Members who need leverage will look for your badges:\n\n"
                "• ⚡ **Growth & Sales** — Copywriting, funnels, outbound, client acquisition\n"
                "• 🛠️ **Systems & Code** — AI, automations, high-performance architecture\n"
                "• 📈 **Capital & Finance** — Deal structuring, treasury, pricing models\n"
                "• 🎨 **Product & Design** — UX/UI, branding, high-conversion aesthetics\n\n"
                "*Click the buttons below to toggle your domain badges.*"
            ),
            color=0x1ABC9C
        )
        
        # Superpower view buttons
        class SuperpowerSelectView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @discord.ui.button(label="Growth & Sales", style=discord.ButtonStyle.primary, emoji="⚡", custom_id="role_growth")
            async def growth_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
                pass
            @discord.ui.button(label="Systems & Code", style=discord.ButtonStyle.primary, emoji="🛠️", custom_id="role_systems")
            async def systems_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
                pass
            @discord.ui.button(label="Capital & Finance", style=discord.ButtonStyle.primary, emoji="📈", custom_id="role_capital")
            async def capital_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
                pass
            @discord.ui.button(label="Product & Design", style=discord.ButtonStyle.primary, emoji="🎨", custom_id="role_product")
            async def product_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
                pass

        await channel.send(embed=embed, view=SuperpowerSelectView())
        print("Posted interactive menu to #superpower-exchange!")
    await client.close()

client.run(TOKEN)
