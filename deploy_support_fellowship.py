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

print("1. Fetching server structure...")
channels = api_call(f"/guilds/{GUILD_ID}/channels")
roles = api_call(f"/guilds/{GUILD_ID}/roles")

channel_map = {c["name"]: c["id"] for c in channels}
role_map = {r["name"]: r["id"] for r in roles}

VIEW_CHANNEL = 1 << 10
SEND_MESSAGES = 1 << 11
READ_MESSAGE_HISTORY = 1 << 16

everyone_role_id = role_map.get("@everyone", GUILD_ID)
partner_role_id = role_map.get("Consortium Partner")
board_role_id = role_map.get("Executive Advisory Board")
managing_role_id = role_map.get("Managing Partner")
prospect_role_id = role_map.get("Prospective Member")

# 2. Add New Roles: Research Fellow, Academic & Technical Scholar
new_roles_needed = [
    ("Research Fellow", 0x38BDF8, True),            # Sky Blue / Academic Fellow
    ("Technical Scholar", 0xA7F3D0, False)          # Mint / Student Builder
]

for r_name, r_color, r_hoist in new_roles_needed:
    if r_name not in role_map:
        res = api_call(f"/guilds/{GUILD_ID}/roles", method="POST", data={
            "name": r_name,
            "color": r_color,
            "hoist": r_hoist,
            "mentionable": True
        })
        role_map[r_name] = res["id"]
        print(f"Created role: {r_name}")
        time.sleep(0.3)

# 3. Create Category: 🎓 // FELLOWSHIPS, RESEARCH & TECHNICAL ADVISORY
category_name = "🎓 // FELLOWSHIPS & TECHNICAL ADVISORY"
fellowship_cat_id = None
for c in channels:
    if c["type"] == 4 and "FELLOWSHIPS" in c["name"]:
        fellowship_cat_id = c["id"]
        break

if not fellowship_cat_id:
    # Visible to all cleared members and prospective members so students/researchers can see it!
    overwrites = [
        {"id": everyone_role_id, "type": 0, "allow": str(VIEW_CHANNEL | SEND_MESSAGES | READ_MESSAGE_HISTORY), "deny": "0"}
    ]
    cat_payload = {
        "name": category_name,
        "type": 4,
        "permission_overwrites": overwrites
    }
    cat = api_call(f"/guilds/{GUILD_ID}/channels", method="POST", data=cat_payload)
    fellowship_cat_id = cat["id"]
    print(f"Created category: {category_name}")

# Channels to create under this category
fellowship_channels = [
    ("research-fellowships-and-internships", "Legitimate corporate-sponsored research internships and pure open-ended domain grants."),
    ("technical-and-repo-guidance", "Deep code reviews, system architecture unblocking, and AI/repo assistance for student & frontier builders."),
    ("academic-and-capstone-advisory", "Guidance on collegiate capstone projects, academic thesis papers, and high-level career positioning."),
    ("executive-escalation-and-support", "Direct line to Consortium Directorate for any blocker where genuine level-up is on the line.")
]

for ch_name, topic in fellowship_channels:
    if ch_name not in channel_map:
        ch_payload = {
            "name": ch_name,
            "type": 0,
            "parent_id": fellowship_cat_id,
            "topic": topic
        }
        res = api_call(f"/guilds/{GUILD_ID}/channels", method="POST", data=ch_payload)
        channel_map[ch_name] = res["id"]
        print(f"Created channel: #{ch_name}")
        time.sleep(0.3)

print("\n4. Deploying Structured Embeds...")

# Channel 1: Research Fellowships & Legitimate Corporate Internships
if "research-fellowships-and-internships" in channel_map:
    rf_id = channel_map["research-fellowships-and-internships"]
    embed = {
        "title": "RESEARCH FELLOWSHIPS & LEGITIMATE CORPORATE INTERNSHIPS",
        "description": (
            "### The ALL-SIGNAL Research Mandate\n"
            "We reject exploitative corporate grunt work. The **ALL-SIGNAL Directorate** sponsors legitimate corporate internship credentials "
            "backed by registered enterprise entities, built around one simple thesis:\n\n"
            "> **“Pure research and genuine execution on whatever frontier topic you obsess over.”**\n\n"
            "You do not fetch coffee or format spreadsheets. If you are passionate about LLM mechanistic interpretability, distributed consensus, "
            "custom robotics, algorithmic execution, or high-performance systems — we provide the legal corporate wrapper, institutional backing, "
            "and legitimate experience credits.\n\n"
            "### What We Provide:\n"
            "• **Legitimate Corporate Credentials:** Verifiable corporate internship completion certificates, formal recommendation letters, and founder references.\n"
            "• **Pure Research Autonomy:** Complete freedom to select your research objective, open-source codebase, or venture thesis.\n"
            "• **Direct Mentorship:** Continuous feedback from senior engineers and fund managers.\n\n"
            "### How to Apply for Fellowship Clearance:\n"
            "Post your pitch in this channel with:\n"
            "```yaml\n"
            "Obsession: [Exact technical/frontier domain you want to research]\n"
            "Proposed Deliverable: [Open-source repo / technical whitepaper / working prototype]\n"
            "Timeline: [e.g. 8-12 weeks]\n"
            "GitHub / Prior Work: [Link to any code, repo, or writing]\n"
            "```"
        ),
        "color": 0x38BDF8,
        "footer": {"text": "ALL-SIGNAL Research Directorate // Verified Fellowships"}
    }
    api_call(f"/channels/{rf_id}/messages", method="POST", data={"embeds": [embed]})
    print("Posted Research Fellowships embed.")
    time.sleep(0.4)

# Channel 2: Technical & Repo Guidance
if "technical-and-repo-guidance" in channel_map:
    tr_id = channel_map["technical-and-repo-guidance"]
    embed = {
        "title": "TECHNICAL ADVISORY // ARCHITECTURE & REPO CLINIC",
        "description": (
            "### For Students & Frontier Engineers Building Systems\n"
            "If you are stuck on a difficult technical bottleneck while building an AI framework, complex backend, compiler, or algorithm — "
            "you have access to senior architects across the Consortium.\n\n"
            "### What We Assist With:\n"
            "• **Architecture Review:** System design diagrams, database schema optimization, latency reduction.\n"
            "• **Code & Repo Diagnostics:** Debugging race conditions, CUDA/PyTorch memory bottlenecks, distributed scaling issues.\n"
            "• **Tooling & Cloud Leverage:** Guidance on deploying high-scale infrastructure cleanly without burning unnecessary capital.\n\n"
            "*Drop your repo link, architecture diagram, or specific blocker below for deep technical review.*"
        ),
        "color": 0xA7F3D0,
        "footer": {"text": "Consortium Technical Working Group"}
    }
    api_call(f"/channels/{tr_id}/messages", method="POST", data={"embeds": [embed]})
    print("Posted Technical Guidance embed.")
    time.sleep(0.4)

# Channel 3: Academic & Capstone Advisory
if "academic-and-capstone-advisory" in channel_map:
    ac_id = channel_map["academic-and-capstone-advisory"]
    embed = {
        "title": "ACADEMIC & CAPSTONE ADVISORY // STUDENT FORUM",
        "description": (
            "### Bridging College Projects to Frontier Enterprise Reality\n"
            "Too many student projects remain generic CRUD apps that fail to impress enterprise recruiters or investors. "
            "We help college students transform routine academic requirements into breakthrough portfolio anchors.\n\n"
            "### Support Pillars:\n"
            "• **Capstone Conception:** Elevating ordinary degree projects into novel frontier applications.\n"
            "• **Technical Paper Structuring:** Guidance on LaTeX drafting, benchmark evaluations, and empirical rigor.\n"
            "• **Career Positioning:** Direct coaching on cracking top-tier research labs and high-compensation engineering roles.\n\n"
            "*Ask any academic, collegiate, or early-career technical question here.*"
        ),
        "color": 0xF1C40F,
        "footer": {"text": "Academic Directorate"}
    }
    api_call(f"/channels/{ac_id}/messages", method="POST", data={"embeds": [embed]})
    print("Posted Academic Advisory embed.")
    time.sleep(0.4)

# Channel 4: The Sovereign Support Covenant
if "executive-escalation-and-support" in channel_map:
    ees_id = channel_map["executive-escalation-and-support"]
    embed = {
        "title": "THE ALL-SIGNAL SUPPORT COVENANT // THE SOVEREIGN GUARANTEE",
        "description": (
            "### The Directorate's Commitment\n"
            "The leadership and backend group of **ALL-SIGNAL** stand behind every dedicated builder in this ecosystem.\n\n"
            "### Our Unconditional Guarantee:\n"
            "> **“Whatever your problem — technical roadblocks, university capstone friction, commercial deal structuring, career navigation, or venture launch — our authority and network will step in to unblock you, provided one condition is met:”**\n\n"
            "### ⚖️ The Sole Condition: Genuine Level-Up\n"
            "We do not solve homework for slackers or validate lazy shortcuts. But if you have genuine ambition, high cognitive hunger, "
            "and are working to achieve a **real, permanent level-up in your life and craft**, you have the full backing of our enterprise infrastructure.\n\n"
            "**How to Escalate:**\n"
            "1. Post your situation directly in this channel or ping `@Managing Partner`.\n"
            "2. State your objective, what you've tried so far, and the specific wall you hit.\n"
            "3. The Directorate will assign senior technical or executive partners to resolve the bottleneck."
        ),
        "color": 0x1F2937,
        "footer": {"text": "ALL-SIGNAL Executive Directorate // Sovereign Support Pledge"}
    }
    api_call(f"/channels/{ees_id}/messages", method="POST", data={"embeds": [embed]})
    print("Posted Executive Escalation & Support Covenant.")

print("\nFellowship & Support architecture finalized successfully!")
