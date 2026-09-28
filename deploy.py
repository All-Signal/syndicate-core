from dotenv import load_dotenv
import os
load_dotenv()
import urllib.request
import json
import time
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID", "1554105137855729724")
BASE_URL = "https://discord.com/api/v10"

headers = {
    "Authorization": f"Bot {TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "DiscordBot (https://discord.com, v10)"
}

def api_call(path, method="GET", data=None):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers=headers, method=method)
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        req.data = body
    
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
                retry_after = err_json.get("retry_after", 1.0)
                print(f"[Rate limit] sleeping {retry_after}s...")
                time.sleep(retry_after)
                continue
            else:
                print(f"HTTPError {e.code} on {method} {path}: {err_body}")
                raise e

print("1. Fetching existing state...")
existing_channels = api_call(f"/guilds/{GUILD_ID}/channels")

# Delete default boilerplate channels
for ch in existing_channels:
    print(f"Deleting default channel: {ch['name']} ({ch['id']})")
    try:
        api_call(f"/channels/{ch['id']}", method="DELETE")
        time.sleep(0.5)
    except Exception as e:
        print(f"Could not delete {ch['name']}: {e}")

print("\n2. Creating Roles...")
roles_config = [
    # (name, color_hex, hoist, mentionable)
    ("[ 0 ] Core Architect", 0x9B59B6, True, True),      # Purple / Obsidian
    ("[ I ] The Council", 0xE67E22, True, True),          # Deep Amber / Gold
    ("[ II ] Syndicate Member", 0x1ABC9C, True, True),    # Teal / Cyan
    ("[ III ] Initiate", 0x95A5A6, True, False),          # Slate / Grey
    ("⚡ Growth & Sales", 0xF1C40F, False, True),
    ("🛠️ Systems & Code", 0x3498DB, False, True),
    ("📈 Capital & Finance", 0x2ECC71, False, True),
    ("🎨 Product & Design", 0xE91E63, False, True),
]

created_roles = {}
for name, color, hoist, mentionable in roles_config:
    data = {
        "name": name,
        "color": color,
        "hoist": hoist,
        "mentionable": mentionable
    }
    r = api_call(f"/guilds/{GUILD_ID}/roles", method="POST", data=data)
    created_roles[name] = r["id"]
    print(f"Created role: {name} -> {r['id']}")
    time.sleep(0.4)

print("\n3. Creating Categories & Channels...")

structure = [
    {
        "category": "📜 // THE PROTOCOL",
        "channels": [
            ("manifesto", 0, "The founding philosophy, ethos, and oath of THE ONE."),
            ("rules-of-engagement", 0, "High signal guidelines, radical candor, zero spam policy."),
            ("announcements", 0, "High-level syndicate broadcasts, drops, and ecosystem updates.")
        ]
    },
    {
        "category": "🚪 // THE THRESHOLD",
        "channels": [
            ("introductions", 0, "State your obsession, what you are building, and where you need leverage."),
            ("proof-of-work", 0, "Post live links, revenue dashboards, repos, or projects you have shipped.")
        ]
    },
    {
        "category": "🚀 // INCUBATION & ESCALATION",
        "channels": [
            ("first-blood", 0, "Zero-to-one: Getting your first client, initial sales, and first traction."),
            ("offer-and-pricing", 0, "Roast & refine client offers, retainers, margins, and packaging."),
            ("growth-and-funnels", 0, "Cold outreach, viral distribution, conversion loops, and paid ads."),
            ("client-referrals", 0, "Pass vetted deals, overflow leads, and client opportunities internally."),
            ("win-board", 0, "Contracts signed, ARR unlocked, launches shipped. Celebrate the wins.")
        ]
    },
    {
        "category": "🤝 // SYNDICATE COLLABORATION",
        "channels": [
            ("co-founder-and-teams", 0, "Pairing technical architects with ruthless distribution & sales minds."),
            ("superpower-exchange", 0, "Trade asymmetric skills: code for copy, automations for sales."),
            ("resource-vault", 0, "Vetted templates, cold email scripts, contract models, and decks.")
        ]
    },
    {
        "category": "🧠 // SYNAPSES (OPEN FORUM)",
        "channels": [
            ("the-nexus", 0, "High-velocity intellectual discourse, general thoughts, real-time banter."),
            ("hyperfocus", 0, "Obscure rabbit holes, 20-page analyses, deep-dive thesis papers."),
            ("raw-thoughts", 0, "Unfiltered 2 AM epiphanies, manic brainstorms, untamed mental models.")
        ]
    },
    {
        "category": "🔬 // DOMAIN LABS",
        "channels": [
            ("frontier-ai-and-tech", 0, "Autonomous agents, LLM architectures, robotics, infrastructure."),
            ("quant-and-capital", 0, "Markets, liquidity, algorithmic execution, crypto, cash flow."),
            ("human-optimization", 0, "Neurochemistry, sleep architectures, energy protocols, nootropics.")
        ]
    },
    {
        "category": "🎙️ // FREQUENCY (VOICE)",
        "channels": [
            ("The War Room", 2, "Live pitch reviews, client closing strategy calls."),
            ("Co-Working Bunker", 2, "Silent accountability and sprint execution."),
            ("Open Frequency", 2, "Spontaneous late-night discussions and high-signal masterminds.")
        ]
    }
]

created_channels = {}
for section in structure:
    cat_name = section["category"]
    cat_payload = {
        "name": cat_name,
        "type": 4 # GUILD_CATEGORY
    }
    cat = api_call(f"/guilds/{GUILD_ID}/channels", method="POST", data=cat_payload)
    cat_id = cat["id"]
    print(f"\nCreated Category: {cat_name} ({cat_id})")
    time.sleep(0.5)

    for ch_name, ch_type, topic in section["channels"]:
        ch_payload = {
            "name": ch_name,
            "type": ch_type,
            "parent_id": cat_id,
            "topic": topic
        }
        ch = api_call(f"/guilds/{GUILD_ID}/channels", method="POST", data=ch_payload)
        created_channels[ch_name] = ch["id"]
        print(f"  └─ Created Channel: #{ch_name} (type: {ch_type})")
        time.sleep(0.4)

print("\n4. Posting Welcome Embeds & Manifesto...")

# Post Manifesto
if "manifesto" in created_channels:
    manifesto_embed = {
        "title": "THE ONE // MANIFESTO",
        "description": (
            "> *“Chaos is not a disorder to be cured. It is unchanneled compute waiting for an architecture.”*\n\n"
            "**Welcome to THE ONE.**\n\n"
            "This society exists for high-cognitive velocity minds who do not fit into the linear structures of conventional life. "
            "If you have felt intellectually isolated, labeled as 'unfocused' because of your obsessive deep dives, or struggled to find peers who operate at your speed — you have found your enclave.\n\n"
            "### 🏛️ The Three Pillars\n"
            "1. **High-Velocity Intellect:** We reject small talk and superficial chatter. We celebrate hyper-fixations, rabbit holes, and asymmetric thinking.\n"
            "2. **Relentless Execution:** Raw brilliance without execution is vanity. Every mind here builds, ships, or allocates capital.\n"
            "3. **Mutual Escalation:** We are an internal economic engine. We trade superpowers — technical architects pair with growth alchemists to close clients, scale businesses, and build sovereign empires.\n\n"
            "— *The Architects*"
        ),
        "color": 0x9B59B6,
        "footer": {"text": "THE ONE // Syndicate Protocol"}
    }
    api_call(f"/channels/{created_channels['manifesto']}/messages", method="POST", data={"embeds": [manifesto_embed]})
    time.sleep(0.5)

# Post Rules
if "rules-of-engagement" in created_channels:
    rules_embed = {
        "title": "RULES OF ENGAGEMENT",
        "description": (
            "**I. High Signal-to-Noise Ratio**\n"
            "Keep discussions substantive. Add context, bring receipts, and elevate the room.\n\n"
            "**II. Radical Candor & Ground Truth**\n"
            "Egos are checked at the threshold. Roast ideas ruthlessly to make them bulletproof, but always respect the builder.\n\n"
            "**III. Givers Gain (The Escalation Principle)**\n"
            "Contribute leverage before asking for it. Share leads, unblock peers, and refer clients.\n\n"
            "**IV. Zero Tolerance for Grifters**\n"
            "No unsolicited DMs, no low-effort self-promotion, no fake gurus. Verified builders only."
        ),
        "color": 0x1ABC9C,
        "footer": {"text": "Protocol Enforced"}
    }
    api_call(f"/channels/{created_channels['rules-of-engagement']}/messages", method="POST", data={"embeds": [rules_embed]})
    time.sleep(0.5)

# Post Intro Prompt
if "introductions" in created_channels:
    intro_embed = {
        "title": "INITIALIZE CONNECTION // INTRODUCTION TEMPLATE",
        "description": (
            "Drop your introduction using this format:\n\n"
            "```yaml\n"
            "Obsession: [What takes up 80% of your cognitive bandwidth?]\n"
            "Superpower: [What is your 99th-percentile skill?]\n"
            "Current Build: [What business, system, or project are you shipping?]\n"
            "Where You Need Leverage: [Sales, tech, distribution, capital, or ops?]\n"
            "Proof of Work: [Links, repos, sites, or track record]\n"
            "```"
        ),
        "color": 0xE67E22,
        "footer": {"text": "Step across the threshold."}
    }
    api_call(f"/channels/{created_channels['introductions']}/messages", method="POST", data={"embeds": [intro_embed]})
    time.sleep(0.5)

# Post First Blood Guide
if "first-blood" in created_channels:
    first_blood_embed = {
        "title": "🩸 FIRST BLOOD // THE ZERO-TO-ONE ACCELERATOR",
        "description": (
            "This channel is dedicated to the hardest step in any venture: **the first transaction**.\n\n"
            "• Getting your first high-ticket retainer\n"
            "• Sourcing your first 5 beta clients\n"
            "• Overcoming analysis paralysis and sending cold outreach\n"
            "• Pitching and live objection handling\n\n"
            "*Post your offer here if you need it dissected and optimized for closing.*"
        ),
        "color": 0xF1C40F,
        "footer": {"text": "Move from theory to revenue."}
    }
    api_call(f"/channels/{created_channels['first-blood']}/messages", method="POST", data={"embeds": [first_blood_embed]})
    time.sleep(0.5)

print("\n✅ Server deployment complete!")
