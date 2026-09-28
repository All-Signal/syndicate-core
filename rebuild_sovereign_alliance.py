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

print("1. Fetching server channels...")
channels = api_call(f"/guilds/{GUILD_ID}/channels")
roles = api_call(f"/guilds/{GUILD_ID}/roles")

channel_map = {c["name"]: c["id"] for c in channels}
role_map = {r["name"]: r["id"] for r in roles}

VIEW_CHANNEL = 1 << 10
SEND_MESSAGES = 1 << 11
READ_MESSAGE_HISTORY = 1 << 16
everyone_role_id = role_map.get("@everyone", GUILD_ID)

# 2. Rename Category to Sovereign Alliance & Full-Spectrum Support
cat_id = None
for c in channels:
    if c["type"] == 4 and "FELLOWSHIPS" in c["name"]:
        cat_id = c["id"]
        break

NEW_CATEGORY_NAME = "🏛️ // THE ALLIANCE (FULL-SPECTRUM SUPPORT)"
if cat_id:
    api_call(f"/channels/{cat_id}", method="PATCH", data={"name": NEW_CATEGORY_NAME})
    print(f"Renamed category to: {NEW_CATEGORY_NAME}")
else:
    overwrites = [
        {"id": everyone_role_id, "type": 0, "allow": str(VIEW_CHANNEL | SEND_MESSAGES | READ_MESSAGE_HISTORY), "deny": "0"}
    ]
    res = api_call(f"/guilds/{GUILD_ID}/channels", method="POST", data={
        "name": NEW_CATEGORY_NAME,
        "type": 4,
        "permission_overwrites": overwrites
    })
    cat_id = res["id"]

# 3. Clean, institutional channel names reflecting full-spectrum backing
target_channels = [
    ("the-sovereign-covenant", "The foundational pact: Unconditional alliance, backing, and leverage across any arena of life."),
    ("research-fellowships-and-credentials", "Legitimate corporate-backed internships and unrestricted research fellowships for pure passion."),
    ("technical-and-systems-clinic", "Deep-tier engineering, AI architecture, code reviews, and student repo unblocking."),
    ("life-and-strategic-advisory", "High-level counsel on career pivots, collegiate friction, negotiations, resilience, and personal expansion."),
    ("direct-directorate-dispatch", "Direct escalation channel to Consortium Leadership for urgent, critical-path unblocking.")
]

existing_sub_channels = [c for c in channels if c.get("parent_id") == cat_id]
for sc in existing_sub_channels:
    try:
        api_call(f"/channels/{sc['id']}", method="DELETE")
        print(f"Pruned prior channel: #{sc['name']}")
        time.sleep(0.3)
    except Exception as e:
        print(f"Error pruning {sc['name']}: {e}")

created_ch_ids = {}
for ch_name, topic in target_channels:
    payload = {
        "name": ch_name,
        "type": 0,
        "parent_id": cat_id,
        "topic": topic
    }
    c_res = api_call(f"/guilds/{GUILD_ID}/channels", method="POST", data=payload)
    created_ch_ids[ch_name] = c_res["id"]
    print(f"Created channel: #{ch_name}")
    time.sleep(0.4)

print("\n4. Deploying Master Sovereign Covenant Embeds...")

# Channel 1: The Sovereign Covenant (Master Document)
if "the-sovereign-covenant" in created_ch_ids:
    covenant_embed = {
        "title": "🏛️ THE SOVEREIGN ALLIANCE // FULL-SPECTRUM SUPPORT COVENANT",
        "description": (
            "# We Stand Behind Our People In Every Arena Of Life.\n\n"
            "The leadership and backend authority of **ALL-SIGNAL** do not run a casual forum or a passive chatroom. "
            "We operate as a **Sovereign Mutual Defense and Acceleration Alliance**.\n\n"
            "Too often, relentless minds are forced to navigate the world alone—facing institutional gatekeepers, technical walls, "
            "academic bureaucracy, commercial hostility, or personal burnout with zero backup. **That ends here.**\n\n"
            "---\n\n"
            "### 🛡️ OUR PLEDGE: UNRESTRICTED ALLIANCE & LEVERAGE\n"
            "We provide strength, backing, and high-level intervention across **ANY category, field, or dimension of life**, including but not limited to:\n\n"
            "• **Academic & Collegiate Battles:** Capstone designs, university disputes, research theses, navigating admissions, or pivoting out of stale curricula.\n"
            "• **Frontier Technical Architecture:** Debugging complex repos, optimizing AI/LLM models, distributed systems, CUDA bottlenecks, or securing compute.\n"
            "• **Corporate Standing & Fellowships:** Providing legitimate, legal corporate-backed internships and research credentials from registered companies—with **total freedom** to pursue pure, genuine research on whatever domain you love.\n"
            "• **Commercial & Strategic Leverage:** Sourcing high-ticket clients, negotiating salary/equity, reviewing contracts, venture launches, or corporate defense.\n"
            "• **Life, Mindset & Personal Resilience:** Handling cognitive burnout, high-stakes decisions, focus management, or standing firm against environments that try to shrink you.\n\n"
            "---\n\n"
            "### ⚖️ THE SOLE CONDITION: GENUINE LEVEL-UP\n"
            "> **“We will mobilize our full network, authority, capital, and engineering power to solve ANY problem in your path—provided it serves your genuine, permanent level-up.”**\n\n"
            "We do not facilitate laziness, entitlement, or shortcuts. But if you have true hunger, integrity, and the courage to build a sovereign future, "
            "**you will never fight a wall alone again.**\n\n"
            "— *The Executive Directorate & Backend Council, ALL-SIGNAL Consortium*"
        ),
        "color": 0x1F2937,
        "footer": {"text": "ALL-SIGNAL Sovereign Alliance // Binding Directorate Covenant"}
    }
    msg = api_call(f"/channels/{created_ch_ids['the-sovereign-covenant']}/messages", method="POST", data={"embeds": [covenant_embed]})
    # Pin covenant
    try:
        api_call(f"/channels/{created_ch_ids['the-sovereign-covenant']}/pins/{msg['id']}", method="PUT")
    except Exception:
        pass
    print("Posted & pinned master covenant.")

# Channel 2: Research Fellowships & Credentials
if "research-fellowships-and-credentials" in created_ch_ids:
    fellowship_embed = {
        "title": "CORPORATE RESEARCH FELLOWSHIPS // PASSION-DRIVEN MANDATE",
        "description": (
            "### Real Enterprise Credentials. Zero Corporate Grunt Work.\n"
            "To support our builders, researchers, and students, the Consortium provides **legitimate corporate research internships** "
            "backed by registered corporate entities.\n\n"
            "**The Philosophy:**\n"
            "Traditional corporate internships force talented minds into monotonous spreadsheet formatting and low-leverage grunt work. "
            "We do the exact opposite:\n\n"
            "> **You choose the topic you are genuinely obsessed with. We provide the institutional corporate backing, legal credentials, and senior advisory.**\n\n"
            "Whether your obsession is AI mechanistic interpretability, distributed databases, algorithmic finance, robotics, or novel web architectures:\n"
            "• Official corporate experience letters and employment verification.\n"
            "• Verifiable founder recommendations and portfolio backing.\n"
            "• Complete autonomy over your research output.\n\n"
            "*Submit your research focus or internship request here.*"
        ),
        "color": 0x38BDF8,
        "footer": {"text": "Verified Corporate Fellowships"}
    }
    api_call(f"/channels/{created_ch_ids['research-fellowships-and-credentials']}/messages", method="POST", data={"embeds": [fellowship_embed]})
    print("Posted Research Fellowships embed.")

# Channel 3: Technical & Systems Clinic
if "technical-and-systems-clinic" in created_ch_ids:
    tech_embed = {
        "title": "TECHNICAL & SYSTEMS CLINIC // CODE, AI & REPO UNBLOCKING",
        "description": (
            "### No Technical Problem Is Out Of Bounds.\n"
            "Whether you are a university student building a breakthrough capstone or a frontier engineer architecting a production system, "
            "you have access to battle-tested senior engineers.\n\n"
            "**Drop your repo, architecture, or obstacle here:**\n"
            "• System design reviews and schema stress-testing\n"
            "• AI/ML model tuning, dataset pipelines, and CUDA optimizations\n"
            "• Hard bugs, race conditions, memory leaks, and deployment infrastructure\n\n"
            "*Include context, what you've tried, and your target deliverable.*"
        ),
        "color": 0x0D9488,
        "footer": {"text": "Consortium Engineering Wing"}
    }
    api_call(f"/channels/{created_ch_ids['technical-and-systems-clinic']}/messages", method="POST", data={"embeds": [tech_embed]})
    print("Posted Technical Clinic embed.")

# Channel 4: Life & Strategic Advisory
if "life-and-strategic-advisory" in created_ch_ids:
    life_embed = {
        "title": "STRATEGIC ADVISORY // ALL-SPECTRUM LIFE COUNSEL",
        "description": (
            "### Navigating High-Stakes Pivots, Pressures & Ambition.\n"
            "Technical mastery without life leverage leads to burnout. This channel is dedicated to navigating the human, strategic, "
            "and psychological challenges of high-agency living:\n\n"
            "• High-stakes career pivots and compensation negotiations\n"
            "• Resolving academic and bureaucratic disputes with university administrations\n"
            "• Overcoming cognitive exhaustion, focus scatter, and intense hyper-fixation burnout\n"
            "• Crafting an unshakeable sovereign trajectory\n\n"
            "*Speak candidly. All discussions in this chamber are held under strict syndicate confidentiality.*"
        ),
        "color": 0xD97706,
        "footer": {"text": "Executive Advisory Group"}
    }
    api_call(f"/channels/{created_ch_ids['life-and-strategic-advisory']}/messages", method="POST", data={"embeds": [life_embed]})
    print("Posted Life & Strategic Advisory embed.")

# Channel 5: Direct Directorate Dispatch
if "direct-directorate-dispatch" in created_ch_ids:
    dispatch_embed = {
        "title": "DIRECT DIRECTORATE DISPATCH // CRITICAL ESCALATIONS",
        "description": (
            "### Direct Line To Consortium Leadership.\n"
            "When you hit a critical barrier that threatens your growth, project, or forward momentum:\n\n"
            "1. Post the situation here detailing the core friction.\n"
            "2. State the exact outcome required for your level-up.\n"
            "3. The Managing Partner and Executive Council will step in with direct intervention, introductions, or institutional backing."
        ),
        "color": 0xDC2626,
        "footer": {"text": "Direct High-Clearance Line"}
    }
    api_call(f"/channels/{created_ch_ids['direct-directorate-dispatch']}/messages", method="POST", data={"embeds": [dispatch_embed]})
    print("Posted Direct Dispatch embed.")

print("\nSovereign Alliance overhaul complete!")
