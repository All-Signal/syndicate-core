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
    "managing_partner": "Managing Partner",
    "advisory_board": "Executive Advisory Board",
    "consortium_partner": "Consortium Partner",
    "prospective_member": "Prospective Member",
    "growth": "Growth & Distribution",
    "engineering": "Engineering & Infrastructure",
    "capital": "Capital Markets & Treasury",
    "product": "Product Strategy & Design"
}

# 1. Interactive Button View for Self-Selecting Competency Badges
class CapabilitySelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Growth & Distribution", style=discord.ButtonStyle.primary, emoji="📈", custom_id="role_growth")
    async def growth_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, ROLE_NAMES["growth"])

    @discord.ui.button(label="Engineering & Infrastructure", style=discord.ButtonStyle.primary, emoji="🛠️", custom_id="role_eng")
    async def eng_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, ROLE_NAMES["engineering"])

    @discord.ui.button(label="Capital Markets & Treasury", style=discord.ButtonStyle.primary, emoji="🏛️", custom_id="role_capital")
    async def capital_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._toggle_role(interaction, ROLE_NAMES["capital"])

    @discord.ui.button(label="Product Strategy & Design", style=discord.ButtonStyle.primary, emoji="📐", custom_id="role_product")
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
            await interaction.response.send_message(f"Removed specialization: **{role.name}**", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"Confirmed specialization: **{role.name}**", ephemeral=True)

# 2. Interactive Admissions Committee Review Station
class AdmissionsApprovalView(discord.ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(label="Grant Consortium Clearance", style=discord.ButtonStyle.success, emoji="✅", custom_id="admissions_approve")
    async def approve_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.applicant_id)
        if not member:
            try:
                member = await guild.fetch_member(self.applicant_id)
            except Exception:
                await interaction.response.send_message("Candidate no longer in server.", ephemeral=True)
                return

        partner_role = discord.utils.get(guild.roles, name=ROLE_NAMES["consortium_partner"])
        prospect_role = discord.utils.get(guild.roles, name=ROLE_NAMES["prospective_member"])

        if prospect_role and prospect_role in member.roles:
            await member.remove_roles(prospect_role)
        if partner_role:
            await member.add_roles(partner_role)

        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

        await interaction.response.send_message(
            f"✅ **Clearance Ratified:** {member.mention} has been elevated to **{ROLE_NAMES['consortium_partner']}**.",
            ephemeral=False
        )

    @discord.ui.button(label="Request Additional Verification", style=discord.ButtonStyle.danger, emoji="⚠️", custom_id="admissions_reject")
    async def reject_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.applicant_id)
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message(
            f"⚠️ Additional track-record verification requested for {member.mention if member else 'candidate'}.",
            ephemeral=False
        )

# 3. Scheduled Institutional Accountability Engine
@tasks.loop(hours=1)
async def consortium_briefing_engine():
    now = datetime.datetime.now(datetime.timezone.utc)
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return
    
    closed_tx_channel = discord.utils.get(guild.text_channels, name="closed-transactions")
    if not closed_tx_channel:
        return

    # Monday 09:00 UTC Executive Focus Briefing
    if now.weekday() == 0 and now.hour == 9:
        embed = discord.Embed(
            title="EXECUTIVE BRIEFING // WEEKLY OPERATIONAL TARGET",
            description=(
                "**To all Consortium Partners:**\n\n"
                "State your primary commercial objective for this operational cycle:\n\n"
                "• Target commercial deal/contract to execute\n"
                "• Core infrastructure/production release\n"
                "• Capital allocation or treasury milestone\n\n"
                "*Document your objective below. Verification audit convenes Friday.*"
            ),
            color=0x1F2937
        )
        await closed_tx_channel.send(embed=embed)

    # Friday 17:00 UTC Settlement & Transaction Audit
    elif now.weekday() == 4 and now.hour == 17:
        embed = discord.Embed(
            title="OPERATIONAL SETTLEMENT // COMMERCIAL AUDIT",
            description=(
                "**Weekly cycle concluded.**\n\n"
                "Disclose transaction milestones, verified deliverables, or operational bottlenecks encountered during this sprint.\n\n"
                "*Verifiable output over speculative intent.*"
            ),
            color=0xD97706
        )
        await closed_tx_channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})", flush=True)
    bot.add_view(CapabilitySelectView())
    if not consortium_briefing_engine.is_running():
        consortium_briefing_engine.start()

    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} command(s) to guild {GUILD_ID}", flush=True)
    except Exception as e:
        print(f"Failed to sync slash commands: {e}", flush=True)

# Slash Command: Promote partner
@bot.tree.command(name="promote", description="Elevate a member's consortium credentials.")
@app_commands.describe(member="Partner to elevate", tier="Clearance Tier")
@app_commands.choices(tier=[
    app_commands.Choice(name="Consortium Partner (Full Clearance)", value="consortium_partner"),
    app_commands.Choice(name="Executive Advisory Board (Governance)", value="advisory_board"),
])
@app_commands.default_permissions(administrator=True)
async def promote(interaction: discord.Interaction, member: discord.Member, tier: app_commands.Choice[str]):
    role_name = ROLE_NAMES[tier.value]
    target_role = discord.utils.get(interaction.guild.roles, name=role_name)
    prospect_role = discord.utils.get(interaction.guild.roles, name=ROLE_NAMES["prospective_member"])

    if not target_role:
        await interaction.response.send_message(f"Role `{role_name}` not found.", ephemeral=True)
        return

    roles_to_add = [target_role]
    roles_to_remove = []
    if prospect_role and prospect_role in member.roles:
        roles_to_remove.append(prospect_role)

    await member.remove_roles(*roles_to_remove)
    await member.add_roles(*roles_to_add)

    embed = discord.Embed(
        title="CREDENTIAL ELEVATION // ALL-SIGNAL CONSORTIUM",
        description=f"Partner {member.mention} has been elevated to **{target_role.name}**.\nFull executive access granted.",
        color=0x1F2937
    )
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message(f"Successfully elevated {member.name} to {target_role.name}.", ephemeral=True)

# Slash Command: Post an RFP in #rfps-and-contract-awards
@bot.tree.command(name="post_rfp", description="Submit a formal Request for Proposal (RFP) or project award.")
@app_commands.describe(
    scope="Scope of work and core deliverables",
    award="Compensation / contract value (e.g. $10,000 USD / Retainer / Equity)",
    timeline="Project turnaround / delivery date",
    requirements="Technical specifications and qualification criteria"
)
async def post_rfp(interaction: discord.Interaction, scope: str, award: str, timeline: str, requirements: str):
    rfp_channel = discord.utils.get(interaction.guild.text_channels, name="rfps-and-contract-awards")
    if not rfp_channel:
        await interaction.response.send_message("Channel `#rfps-and-contract-awards` not found.", ephemeral=True)
        return

    embed = discord.Embed(
        title="REQUEST FOR PROPOSAL (RFP) // FORMAL CONTRACT DISPATCH",
        description=(
            f"**Deliverable Scope:**\n> {scope}\n\n"
            f"**Contract Award / Budget:**\n> 🏛️ **{award}**\n\n"
            f"**Timeline:**\n> ⏱️ {timeline}\n\n"
            f"**Technical Specifications:**\n> {requirements}\n\n"
            f"**Issuing Partner:** {interaction.user.mention}"
        ),
        color=0x0D9488,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_footer(text="Submit capability dossiers directly to the issuing partner.")
    
    msg = await rfp_channel.send(embed=embed)
    await msg.create_thread(name=f"RFP: {scope[:40]}")
    await interaction.response.send_message(f"RFP dispatched to {rfp_channel.mention}!", ephemeral=True)

# Slash Command: Institutional Oracle Analysis
@bot.tree.command(name="oracle", description="Conduct institutional due diligence, offer audits, or B2B outreach.")
@app_commands.describe(mode="Analysis framework", query="The commercial thesis, offer structure, or enterprise account")
@app_commands.choices(mode=[
    app_commands.Choice(name="🏛️ Due Diligence & Viability Audit", value="brainstorm"),
    app_commands.Choice(name="⚖️ Commercial Offer Structuring & Pricing", value="roast"),
    app_commands.Choice(name="💼 Institutional Enterprise Outreach Architecture", value="outreach")
])
async def oracle(interaction: discord.Interaction, mode: app_commands.Choice[str], query: str):
    await interaction.response.defer(ephemeral=False)
    
    mode_val = mode.value
    if mode_val == "brainstorm":
        embed = discord.Embed(
            title="DUE DILIGENCE MEMORANDUM // VIABILITY AUDIT",
            description=(
                f"**Thesis Under Review:**\n> *\"{query}\"*\n\n"
                "### 🔍 Institutional Evaluation:\n"
                "• **Moat & Defensibility:** How defensible is this against frontier foundation model obsolescence and market saturation?\n"
                "• **Enterprise Switching Friction:** What operational inertia exists within target client systems that could impede deployment?\n"
                "• **Capital Efficiency:** Minimum viable capital requirement to achieve cash-flow breakeven."
            ),
            color=0x1F2937
        )
    elif mode_val == "roast":
        embed = discord.Embed(
            title="OFFER ARCHITECTURE AUDIT // COMMERCIAL TERMS",
            description=(
                f"**Proposed Commercial Offer:**\n> *\"{query}\"*\n\n"
                "### ⚖️ Structuring Recommendations:\n"
                "• **Enterprise Value Framing:** Anchor fees against internal FTE replacement cost and risk-adjusted efficiency yields.\n"
                "• **Contract Structure:** Shift from transactional billing to fixed quarterly retainers with performance equity or milestone bonuses.\n"
                "• **SLA Commitments:** Define clear turnaround boundaries, data governance warranties, and escalation paths."
            ),
            color=0xD97706
        )
    else: # Outreach
        embed = discord.Embed(
            title="ENTERPRISE OUTREACH // ASYMMETRIC B2B FRAMEWORK",
            description=(
                f"**Target Account / Vertical:**\n> *\"{query}\"*\n\n"
                "### 📝 Executive Outreach Architecture:\n"
                "```text\n"
                f"Subject: Brief query regarding {query} infrastructure\n\n"
                f"Dear [Executive Name],\n\n"
                f"Noticed your team's expansion across {query}. "
                "In analogous enterprise environments, scaling this architecture introduced critical latency and cost friction.\n\n"
                "We engineered a specialized deployment pipeline that mitigated this bottleneck for peer institutions, reducing operational overhead by 34%.\n\n"
                "Prepared a brief 2-minute architectural memo detailing the implementation. Would you be open to reviewing the documentation?\n\n"
                "Respectfully,\n"
                "[Your Name]\n"
                "ALL-SIGNAL Consortium\n"
                "```"
            ),
            color=0x0D9488
        )
    embed.set_footer(text=f"Requested by {interaction.user.name} // Directorate Intelligence Engine")
    await interaction.followup.send(embed=embed)

if __name__ == "__main__":
    bot.run(TOKEN)
