from dotenv import load_dotenv
import os
load_dotenv()
import urllib.request
import json
import time

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

channels = api_call(f"/guilds/{GUILD_ID}/channels")
channel_map = {c["name"]: c["id"] for c in channels}

# Check if FREQUENCY category exists
freq_cat_id = channel_map.get("🎙️ // FREQUENCY (VOICE)")
if not freq_cat_id:
    cat_payload = {
        "name": "🎙️ // FREQUENCY (VOICE)",
        "type": 4
    }
    cat = api_call(f"/guilds/{GUILD_ID}/channels", method="POST", data=cat_payload)
    freq_cat_id = cat["id"]
    print(f"Created category FREQUENCY: {freq_cat_id}")

voice_channels = [
    "The War Room",
    "Co-Working Bunker",
    "Open Frequency"
]

for vname in voice_channels:
    if vname not in channel_map:
        vpayload = {
            "name": vname,
            "type": 2, # Voice channel
            "parent_id": freq_cat_id
        }
        res = api_call(f"/guilds/{GUILD_ID}/channels", method="POST", data=vpayload)
        channel_map[vname] = res["id"]
        print(f"Created voice channel: {vname}")
        time.sleep(0.5)

print("\nPosting formatted embeds & system prompts...")

# Manifesto
if "manifesto" in channel_map:
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
    api_call(f"/channels/{channel_map['manifesto']}/messages", method="POST", data={"embeds": [manifesto_embed]})
    time.sleep(0.5)
    print("Posted manifesto embed.")

# Rules
if "rules-of-engagement" in channel_map:
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
    api_call(f"/channels/{channel_map['rules-of-engagement']}/messages", method="POST", data={"embeds": [rules_embed]})
    time.sleep(0.5)
    print("Posted rules embed.")

# Intro Template
if "introductions" in channel_map:
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
    api_call(f"/channels/{channel_map['introductions']}/messages", method="POST", data={"embeds": [intro_embed]})
    time.sleep(0.5)
    print("Posted introduction embed.")

# First Blood
if "first-blood" in channel_map:
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
    api_call(f"/channels/{channel_map['first-blood']}/messages", method="POST", data={"embeds": [first_blood_embed]})
    time.sleep(0.5)
    print("Posted first-blood embed.")

print("\nAll setup actions finalized successfully!")
