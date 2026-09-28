import os
import sys
import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
import datetime

load_dotenv("/home/rudra/discord-server-setup/.env")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "1554105137855729724"))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_NAMES = {
    "architect": "[ 0 ] Core Architect",
    "council": "[ I ] The Council",
    "syndicate": "[ II ] Syndicate Member",
    "initiate": "[ III ] Initiate",
    "growth": "⚡ Growth & Sales",
    "systems": "🛠️ Systems & Code",
    "capital": "📈 Capital & Finance",
    "product": "🎨 Product & Design"
}

# 1. Interactive Button View for Self-Assigning Superpowers
class SuperpowerSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Growth & Sales", style=discord.ButtonStyle.primary, emoji="⚡", custom_id="role_growth")
    async def growth_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, ROLE_NAMES["growth"])

    @discord.ui.button(label="Systems & Code", style=discord.ButtonStyle.primary, emoji="🛠️", custom_id="role_systems")
    async def systems_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, ROLE_NAMES["systems"])

    @discord.ui.button(label="Capital & Finance", style=discord.ButtonStyle.primary, emoji="📈", custom_id="role_capital")
    async def capital_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, ROLE_NAMES["capital"])

    @discord.ui.button(label="Product & Design", style=discord.ButtonStyle.primary, emoji="🎨", custom_id="role_product")
    async def product_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, ROLE_NAMES["product"])

    async def _toggle_role(self, interaction: discord.Interaction, role_name: str):
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            await interaction.response.send_message(f"Role `{role_name}` not found.", ephemeral=True)
            return

        member = interaction.user
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"Removed badge: **{role.name}**", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"Granted badge: **{role.name}** 🚀", ephemeral=True)

# 2. Interactive Vetting View for Approving Proof of Work
class VettingApprovalView(discord.ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(label="Grant Syndicate Clearance", style=discord.ButtonStyle.success, emoji="✅", custom_id="vetting_approve")
    async def approve_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.applicant_id)
        if not member:
            try:
                member = await guild.fetch_member(self.applicant_id)
            except Exception:
                await interaction.response.send_message("Member no longer in server.", ephemeral=True)
                return

        syndicate_role = discord.utils.get(guild.roles, name=ROLE_NAMES["syndicate"])
        initiate_role = discord.utils.get(guild.roles, name=ROLE_NAMES["initiate"])

        if initiate_role and initiate_role in member.roles:
            await member.remove_roles(initiate_role)
        if syndicate_role:
            await member.add_roles(syndicate_role)

        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        await interaction.response.send_message(
            f"✅ **Clearance Approved!** {member.mention} elevated to **{ROLE_NAMES['syndicate']}**.",
            ephemeral=False
        )

    @discord.ui.button(label="Request More Proof", style=discord.ButtonStyle.danger, emoji="⚠️", custom_id="vetting_reject")
    async def reject_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.applicant_id)
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message(
            f"⚠️ Additional proof requested for {member.mention if member else 'user'}.",
            ephemeral=False
        )

# 3. Scheduled Weekly Rituals
@tasks.loop(hours=1)
async def syndicate_ritual_engine():
    now = datetime.datetime.now(datetime.timezone.utc)
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return
    
    win_channel = discord.utils.get(guild.text_channels, name="win-board")
    if not win_channel:
        return

    if now.weekday() == 0 and now.hour == 9:
        embed = discord.Embed(
            title="⚔️ MONDAY PROTOCOL // THE SOVEREIGN OBJECTIVE SPRINT",
            description=(
                "**Attention Syndicate.**\n\n"
                "Chaotic minds default to parallel scatter. For this week, choose **one single sovereign deliverable**:\n\n"
                "• A contract closed\n"
                "• An MVP deployed\n"
                "• 100 cold outreaches sent\n"
                "• A core system automated\n\n"
                "*Reply below with your #1 priority. Friday will demand receipts.*"
            ),
            color=0x9B59B6
        )
        await win_channel.send(embed=embed)

    elif now.weekday() == 4 and now.hour == 17:
        embed = discord.Embed(
            title="🏆 FRIDAY RECKONING // PROOF OF WORK AUDIT",
            description=(
                "**The week has concluded.**\n\n"
                "Did you ship what you committed to on Monday?\n"
                "Post your wins, your dashboards, your deployed repos, or the friction you encountered.\n\n"
                "*No theory. Only shipped reality.*"
            ),
            color=0xF1C40F
        )
        await win_channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})", flush=True)
    bot.add_view(SuperpowerSelectView())
    if not syndicate_ritual_engine.is_running():
        syndicate_ritual_engine.start()

    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} command(s) to guild {GUILD_ID}", flush=True)
    except Exception as e:
        print(f"Failed to sync slash commands: {e}", flush=True)

# Slash Command: Promote member
@bot.tree.command(name="promote", description="Promote a member to Syndicate Member or The Council.")
@app_commands.describe(member="Member to promote", tier="Clearance Tier")
@app_commands.choices(tier=[
    app_commands.Choice(name="Syndicate Member (Full Clearance)", value="syndicate"),
    app_commands.Choice(name="The Council (Leadership / Domain Head)", value="council"),
])
@app_commands.default_permissions(administrator=True)
async def promote(interaction: discord.Interaction, member: discord.Member, tier: app_commands.Choice[str]):
    role_name = ROLE_NAMES[tier.value]
    target_role = discord.utils.get(interaction.guild.roles, name=role_name)
    initiate_role = discord.utils.get(interaction.guild.roles, name=ROLE_NAMES["initiate"])

    if not target_role:
        await interaction.response.send_message(f"Role `{role_name}` not found.", ephemeral=True)
        return

    roles_to_add = [target_role]
    roles_to_remove = []
    if initiate_role and initiate_role in member.roles:
        roles_to_remove.append(initiate_role)

    await member.remove_roles(*roles_to_remove)
    await member.add_roles(*roles_to_add)

    embed = discord.Embed(
        title="CLEARANCE ELEVATION // THE ONE",
        description=f"Member {member.mention} has been elevated to **{target_role.name}**.\nFull syndicate access granted.",
        color=0x9B59B6
    )
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message(f"Successfully elevated {member.name} to {target_role.name}.", ephemeral=True)

# Slash Command: Post a Bounty in #bounties-and-gigs
@bot.tree.command(name="post_bounty", description="Post a structured bounty or gig to the Syndicate economy.")
@app_commands.describe(
    deliverable="What needs to be built or delivered?",
    bounty="Compensation (e.g. $500, 15% rev-share, skill trade)",
    timeline="Turnaround time (e.g. 48 hours, 1 week)",
    requirements="Key tech stack, conditions, or standards"
)
async def post_bounty(interaction: discord.Interaction, deliverable: str, bounty: str, timeline: str, requirements: str):
    bounty_channel = discord.utils.get(interaction.guild.text_channels, name="bounties-and-gigs")
    if not bounty_channel:
        await interaction.response.send_message("Channel `#bounties-and-gigs` not found.", ephemeral=True)
        return

    embed = discord.Embed(
        title="💼 NEW SYNDICATE BOUNTY // OPEN DISPATCH",
        description=(
            f"**Deliverable:**\n> {deliverable}\n\n"
            f"**Compensation / Bounty:**\n> 💰 **{bounty}**\n\n"
            f"**Timeline:**\n> ⏱️ {timeline}\n\n"
            f"**Requirements:**\n> {requirements}\n\n"
            f"**Posted By:** {interaction.user.mention}"
        ),
        color=0x2ECC71,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_footer(text="Reply to this thread or DM the poster to claim.")
    
    msg = await bounty_channel.send(embed=embed)
    await msg.create_thread(name=f"Bounty: {deliverable[:40]}")
    await interaction.response.send_message(f"Bounty published to {bounty_channel.mention}!", ephemeral=True)

# Slash Command: AI Second Brain / Oracle Analysis
@bot.tree.command(name="oracle", description="Dissect a concept, roast an offer, or generate asymmetric cold outreach.")
@app_commands.describe(mode="Analysis mode", query="The offer, idea, or target client to analyze")
@app_commands.choices(mode=[
    app_commands.Choice(name="🧠 Brainstorm & Stress-Test (Find Blindspots)", value="brainstorm"),
    app_commands.Choice(name="🔥 Roast & Refine Offer (Validate Pricing Power)", value="roast"),
    app_commands.Choice(name="⚡ Generate 4-Line Asymmetric Outreach", value="outreach")
])
async def oracle(interaction: discord.Interaction, mode: app_commands.Choice[str], query: str):
    await interaction.response.defer(ephemeral=False)
    
    mode_val = mode.value
    if mode_val == "brainstorm":
        embed = discord.Embed(
            title="🧠 ORACLE // CONCEPT STRESS-TEST",
            description=(
                f"**Thesis Under Examination:**\n> *\"{query}\"*\n\n"
                "### 🔍 Asymmetric Diagnosis:\n"
                "• **The Leverage Angle:** Where is the 10x upside? How does this compound without linear human hours?\n"
                "• **The Vulnerability Point:** What is the hidden friction point? Is customer switching cost too high, or distribution too expensive?\n"
                "• **Zero-to-One Directive:** Do not build the full infrastructure. Build a manual 1-page MVP or prototype script and presell 2 customers before writing boilerplate."
            ),
            color=0x9B59B6
        )
    elif mode_val == "roast":
        embed = discord.Embed(
            title="🔥 ORACLE // OFFER DIAGNOSTIC ROAST",
            description=(
                f"**Proposed Offer:**\n> *\"{query}\"*\n\n"
                "### 🎯 Offer Stress-Test:\n"
                "• **Revenue Distance:** Is this tied to direct revenue/cash preservation, or is it an 'optional luxury'? Always frame it as plugging an active cash bleed.\n"
                "• **Pricing Power:** If you cannot charge $3k+/mo, you are selling labor, not an outcome. Productize the deliverable.\n"
                "• **Reversibility Guarantee:** Add a milestone escrow or risk-reversal (e.g. *'If we don't hit [Metric] by Day 30, we work free until we do'*)."
            ),
            color=0xE67E22
        )
    else: # Outreach
        embed = discord.Embed(
            title="⚡ ORACLE // ASYMMETRIC OUTREACH SCRIPT",
            description=(
                f"**Target Prospect / Domain:**\n> *\"{query}\"*\n\n"
                "### 📝 Generated 4-Line Script:\n"
                "```text\n"
                f"Hey [Name], loved your recent breakdown on [Topic]. Noticed you're scaling {query}.\n"
                "Most teams at your stage hit a massive bottleneck with [Specific Friction Point].\n"
                "We engineered a custom workflow that eliminated this for [Similar Brand], saving ~15h/week.\n"
                "Put together a quick 45s teardown showing how to plug it into your stack — mind if I drop the link?\n"
                "```"
            ),
            color=0x1ABC9C
        )
    embed.set_footer(text=f"Requested by {interaction.user.name} // Syndicate Compute Engine")
    await interaction.followup.send(embed=embed)

# Slash Command: Generate a fresh Vetting Card for an applicant
@bot.tree.command(name="review_applicant", description="Send an applicant to the #syndicate-vetting queue with approval buttons.")
@app_commands.describe(applicant="The applicant to review", proof_link_or_summary="Summary of their proof of work")
@app_commands.default_permissions(administrator=True)
async def review_applicant(interaction: discord.Interaction, applicant: discord.Member, proof_link_or_summary: str):
    vchannel = discord.utils.get(interaction.guild.text_channels, name="syndicate-vetting")
    if not vchannel:
        await interaction.response.send_message("Channel `#syndicate-vetting` not found.", ephemeral=True)
        return

    embed = discord.Embed(
        title="🛡️ APPLICANT DISPATCH // VETTING QUEUE",
        description=(
            f"**Applicant:** {applicant.mention} (`{applicant.name}`)\n"
            f"**Joined:** <t:{int(applicant.joined_at.timestamp())}:R>\n\n"
            f"**Submitted Proof of Work:**\n> {proof_link_or_summary}\n\n"
            "*Click below to grant full Syndicate Clearance or request more proof.*"
        ),
        color=0x9B59B6
    )
    view = VettingApprovalView(applicant_id=applicant.id)
    await vchannel.send(embed=embed, view=view)
    await interaction.response.send_message(f"Review card sent to {vchannel.mention}!", ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)
