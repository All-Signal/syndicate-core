import urllib.request
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID", "1554105137855729724")
BASE_URL = "https://discord.com/api/v10"

headers = {
    "Authorization": f"Bot {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "DiscordBot (https://discord.com, 1.0)"
}

def api_call(path, method="GET", data=None):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers=headers, method=method)
    if data is not None:
        req.data = json.dumps(data).encode("utf-8")
    
    while True:
        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status == 204:
                    return None
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            if e.code == 429:
                err_json = json.loads(err_body)
                time.sleep(err_json.get("retry_after", 1.0))
                continue
            else:
                print(f"HTTPError {e.code} on {method} {path}: {err_body}")
                raise e

print("1. Updating Server Name to 'ALL-SIGNAL // ENTERPRISE CONSORTIUM'...")
api_call(f"/guilds/{GUILD_ID}", method="PATCH", data={
    "name": "ALL-SIGNAL // CONSORTIUM"
})

print("\n2. Renaming Roles to Institutional Corporate-Venture Standard...")
roles = api_call(f"/guilds/{GUILD_ID}/roles")
channels = api_call(f"/guilds/{GUILD_ID}/channels")

role_name_updates = {
    "[ 0 ] Core Architect": "Managing Partner",
    "[ I ] The Council": "Executive Advisory Board",
    "[ II ] Syndicate Member": "Consortium Partner",
    "[ III ] Initiate": "Prospective Member",
    "⚡ Growth & Sales": "Growth & Distribution",
    "🛠️ Systems & Code": "Engineering & Infrastructure",
    "📈 Capital & Finance": "Capital Markets & Treasury",
    "🎨 Product & Design": "Product Strategy & Design"
}

# Distinct, elegant executive hex colors (Deep Slate, Warm Gold, Muted Platinum, Steel)
role_color_updates = {
    "Managing Partner": (0x1F2937, True),          # Deep Executive Charcoal
    "Executive Advisory Board": (0xD97706, True),  # Sovereign Muted Gold
    "Consortium Partner": (0x0D9488, True),        # Deep Muted Emerald/Teal
    "Prospective Member": (0x64748B, True),        # Clean Slate
    "Growth & Distribution": (0xEAB308, False),    # Amber
    "Engineering & Infrastructure": (0x2563EB, False), # Corporate Royal Blue
    "Capital Markets & Treasury": (0x16A34A, False),   # Emerald
    "Product Strategy & Design": (0x9333EA, False)     # Deep Purple
}

for r in roles:
    old_name = r["name"]
    if old_name in role_name_updates:
        new_name = role_name_updates[old_name]
        color, hoist = role_color_updates.get(new_name, (0, False))
        api_call(f"/guilds/{GUILD_ID}/roles/{r['id']}", method="PATCH", data={
            "name": new_name,
            "color": color,
            "hoist": hoist
        })
        print(f"  Role Updated: {old_name} -> {new_name}")
        time.sleep(0.3)

print("\n3. Renaming Categories and Channels to Institutional Grade...")

category_renames = {
    "📜 // THE PROTOCOL": "GOVERNANCE & CHARTER",
    "🚪 // THE THRESHOLD": "MEMBERSHIP ADMISSIONS",
    "🚀 // INCUBATION & ESCALATION": "VENTURE ACCELERATION",
    "🤝 // SYNDICATE COLLABORATION": "PARTNER CO-INVEST & ALLIANCES",
    "🧠 // SYNAPSES (OPEN FORUM)": "RESEARCH & DISCOURSE",
    "🔬 // DOMAIN LABS": "SECTOR WORKING GROUPS",
    "🎙️ // FREQUENCY (VOICE)": "EXECUTIVE SESSIONS (VOICE)",
    "🏛️ // HIGH COUNCIL (GOVERNANCE)": "EXECUTIVE BOARD (RESTRICTED)"
}

channel_renames = {
    "manifesto": "consortium-charter",
    "rules-of-engagement": "operating-principles",
    "announcements": "official-dispatches",
    "introductions": "partner-profiles",
    "proof-of-work": "track-record-verification",
    "syndicate-vetting": "admissions-committee",
    "first-blood": "zero-to-one-traction",
    "offer-and-pricing": "deal-structuring-and-terms",
    "growth-and-funnels": "enterprise-acquisition",
    "client-referrals": "dealflow-syndication",
    "win-board": "closed-transactions",
    "co-founder-and-teams": "leadership-placements",
    "superpower-exchange": "capability-exchange",
    "resource-vault": "intel-and-deal-vault",
    "bounties-and-gigs": "rfps-and-contract-awards",
    "the-nexus": "executive-forum",
    "hyperfocus": "in-depth-theses",
    "raw-thoughts": "unfiltered-intel",
    "frontier-ai-and-tech": "frontier-ai-systems",
    "quant-and-capital": "capital-allocations",
    "human-optimization": "cognitive-performance",
    "council-chamber": "boardroom-briefings",
    "The War Room": "Strategy Session",
    "Co-Working Bunker": "Deep Work Chamber",
    "Open Frequency": "Member Lounge",
    "Council Boardroom": "Executive Boardroom"
}

channel_topics = {
    "consortium-charter": "The founding charter, sovereign standards, and operating ethos of the ALL-SIGNAL Consortium.",
    "operating-principles": "Strict professional decorum, confidentiality covenants, and non-disclosure standards.",
    "official-dispatches": "Executive notices, strategic releases, and consortium milestone reports.",
    "partner-profiles": "Standardized member dossiers detailing primary enterprise, domain competencies, and active objectives.",
    "track-record-verification": "Verifiable repository links, company disclosures, and production credentials for admissions clearance.",
    "admissions-committee": "Private executive admissions review station for Prospective Member clearance.",
    "zero-to-one-traction": "Strategic incubation: closing initial anchor accounts, product validation, and seed traction.",
    "deal-structuring-and-terms": "Pricing power, retainer architecture, SLA definitions, and institutional positioning.",
    "enterprise-acquisition": "Outbound business development, distribution architecture, and scalable pipeline systems.",
    "dealflow-syndication": "B2B client referrals, overflow contracts, and enterprise partnership syndication.",
    "closed-transactions": "Verified commercial contract closings, enterprise launches, and ARR milestones.",
    "leadership-placements": "Strategic co-founder matching, fractional executive recruitment, and cross-enterprise teams.",
    "capability-exchange": "Bilateral capability trading: engineering infrastructure for enterprise distribution.",
    "intel-and-deal-vault": "Proprietary contracts, institutional pitch templates, and legal memorandum frameworks.",
    "rfps-and-contract-awards": "Formal RFPs, paid engineering contracts, and specialized service awards.",
    "executive-forum": "High-signal multi-domain discourse among cleared partners.",
    "in-depth-theses": "Macro-theses, whitepapers, mechanistic architecture analyses, and domain deep dives.",
    "unfiltered-intel": "Asymmetric market observations, frontier hypotheses, and rapid strategic notes.",
    "frontier-ai-systems": "Large-scale foundational systems, autonomous agentic runtimes, and engineering execution.",
    "capital-allocations": "Treasury management, algorithmic finance, liquidity structures, and venture investments.",
    "cognitive-performance": "Operational stamina, sleep architectures, and high-output cognitive frameworks.",
    "boardroom-briefings": "Restricted governance, strategic alliance decisions, and executive reviews."
}

for c in channels:
    c_name = c["name"]
    cid = c["id"]
    if c["type"] == 4: # Category
        if c_name in category_renames:
            new_cat = category_renames[c_name]
            api_call(f"/channels/{cid}", method="PATCH", data={"name": new_cat})
            print(f"  Category Renamed: {c_name} -> {new_cat}")
            time.sleep(0.3)
    else: # Channel
        if c_name in channel_renames:
            new_ch = channel_renames[c_name]
            topic = channel_topics.get(new_ch, "")
            patch_data = {"name": new_ch}
            if c["type"] == 0 and topic:
                patch_data["topic"] = topic
            api_call(f"/channels/{cid}", method="PATCH", data=patch_data)
            print(f"  Channel Renamed: #{c_name} -> #{new_ch}")
            time.sleep(0.3)

print("\n4. Reposting Institutional Charter in #consortium-charter...")
# Find id of consortium-charter
fresh_channels = api_call(f"/guilds/{GUILD_ID}/channels")
charter_id = next((c["id"] for c in fresh_channels if c["name"] == "consortium-charter"), None)
principles_id = next((c["id"] for c in fresh_channels if c["name"] == "operating-principles"), None)

if charter_id:
    charter_embed = {
        "title": "ALL-SIGNAL CONSORTIUM // EXECUTIVE CHARTER",
        "description": (
            "### Preamble\n"
            "The **ALL-SIGNAL Consortium** is an exclusive confederation of sovereign operators, senior systems architects, and venture builders. "
            "We unite divergent, high-velocity cognitive capabilities with institutional-grade commercial execution.\n\n"
            "### Institutional Mandates\n"
            "**1. Meritocratic Clearance & Earned Access:**\n"
            "Access to the Consortium is governed strictly by demonstrable output, shipped software, and validated commercial traction. Speculative theorizing is subordinate to delivered reality.\n\n"
            "**2. Bilateral Leverage & Dealflow Syndication:**\n"
            "The Consortium operates as an internal liquidity and capability market. Partners actively syndicate dealflow, co-invest in high-conviction ventures, and eliminate operational bottlenecks for peer enterprises.\n\n"
            "**3. Absolute Confidentiality:**\n"
            "Discussions within closed working groups, boardroom briefings, and private lab chambers are bound by customary trade-secret and non-disclosure standards.\n\n"
            "— *Executive Directorate, ALL-SIGNAL Consortium*"
        ),
        "color": 0x1F2937,
        "footer": {"text": "ALL-SIGNAL Global Consortium // Governance Code"}
    }
    api_call(f"/channels/{charter_id}/messages", method="POST", data={"embeds": [charter_embed]})
    print("Posted executive charter.")

if principles_id:
    principles_embed = {
        "title": "OPERATING PRINCIPLES & STANDARDS OF CONDUCT",
        "description": (
            "**I. High-Signal Professionalism:**\n"
            "All communications must adhere to institutional standards. Provide substantive data, verifiable citations, and actionable insight.\n\n"
            "**II. Contractual Integrity:**\n"
            "Commitments made in `#rfps-and-contract-awards` or joint syndications must be executed punctually. Delinquency results in immediate revoking of consortium credentials.\n\n"
            "**III. Strict Anti-Solicitation:**\n"
            "Unsolicited retail pitches, automated direct messaging, or non-accredited promotions are strictly prohibited.\n\n"
            "**IV. Constructive Analytical Rigor:**\n"
            "We invite adversarial examination of business models and architectural designs to fortify viability before capital deployment."
        ),
        "color": 0xD97706,
        "footer": {"text": "Enforced by Executive Secretariat"}
    }
    api_call(f"/channels/{principles_id}/messages", method="POST", data={"embeds": [principles_embed]})
    print("Posted operating principles.")

print("\nServer professionalization complete!")
