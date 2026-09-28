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

print("1. Fetching server roles & channels...")
roles = api_call(f"/guilds/{GUILD_ID}/roles")
channels = api_call(f"/guilds/{GUILD_ID}/channels")

role_map = {r["name"]: r["id"] for r in roles}
channel_map = {c["name"]: c["id"] for c in channels}

# Discord Permission Bitflags
VIEW_CHANNEL = 1 << 10
SEND_MESSAGES = 1 << 11
CREATE_PUBLIC_THREADS = 1 << 35
CREATE_PRIVATE_THREADS = 1 << 36
SEND_MESSAGES_IN_THREADS = 1 << 38
ATTACH_FILES = 1 << 15
ADD_REACTIONS = 1 << 6
CONNECT = 1 << 20
SPEAK = 1 << 21
USE_VAD = 1 << 25
PRIORITY_SPEAKER = 1 << 8
MOVE_MEMBERS = 1 << 24
MUTE_MEMBERS = 1 << 22
MANAGE_CHANNELS = 1 << 4
MANAGE_MESSAGES = 1 << 13

# 2. Refine Role Base Permissions
# Initiate: Read basic channels, send text only (cannot attach files or embed links)
initiate_perms = (
    VIEW_CHANNEL | SEND_MESSAGES | ADD_REACTIONS | (1 << 16) # READ_MESSAGE_HISTORY
)
if "[ III ] Initiate" in role_map:
    api_call(f"/guilds/{GUILD_ID}/roles/{role_map['[ III ] Initiate']}", method="PATCH", data={
        "permissions": str(initiate_perms)
    })
    print("Updated Initiate role permissions (Restricted: No embeds, no attachments).")

# Syndicate Member: Full member privileges (attach files, embed links, create threads, speak in voice)
syndicate_perms = (
    VIEW_CHANNEL | SEND_MESSAGES | (1 << 14) | ATTACH_FILES | ADD_REACTIONS | (1 << 16) | # EMBED_LINKS
    CREATE_PUBLIC_THREADS | SEND_MESSAGES_IN_THREADS | CONNECT | SPEAK | USE_VAD
)
if "[ II ] Syndicate Member" in role_map:
    api_call(f"/guilds/{GUILD_ID}/roles/{role_map['[ II ] Syndicate Member']}", method="PATCH", data={
        "permissions": str(syndicate_perms)
    })
    print("Updated Syndicate Member role permissions.")

# The Council: High clearance (Priority Speaker, Mute members, Move members, Manage messages)
council_perms = (
    syndicate_perms | PRIORITY_SPEAKER | MUTE_MEMBERS | MOVE_MEMBERS | MANAGE_MESSAGES
)
if "[ I ] The Council" in role_map:
    api_call(f"/guilds/{GUILD_ID}/roles/{role_map['[ I ] The Council']}", method="PATCH", data={
        "permissions": str(council_perms)
    })
    print("Updated The Council role permissions.")

# 3. Create #council-chamber if missing (Council & Architect Only)
council_cat_id = None
for c in channels:
    if c["type"] == 4 and "THE PROTOCOL" in c["name"]:
        pass

if "the-council-chamber" not in channel_map:
    # Find or create Category for Governance
    gov_cat = api_call(f"/guilds/{GUILD_ID}/channels", method="POST", data={
        "name": "🏛️ // HIGH COUNCIL (GOVERNANCE)",
        "type": 4,
        "permission_overwrites": [
            {"id": role_map["@everyone"], "type": 0, "allow": "0", "deny": str(VIEW_CHANNEL)},
            {"id": role_map["[ I ] The Council"], "type": 0, "allow": str(VIEW_CHANNEL | SEND_MESSAGES | (1 << 16)), "deny": "0"},
            {"id": role_map["[ 0 ] Core Architect"], "type": 0, "allow": str(VIEW_CHANNEL | SEND_MESSAGES | (1 << 16)), "deny": "0"}
        ]
    })
    gov_cat_id = gov_cat["id"]

    # Council Chamber text channel
    c_ch = api_call(f"/guilds/{GUILD_ID}/channels", method="POST", data={
        "name": "council-chamber",
        "type": 0,
        "parent_id": gov_cat_id,
        "topic": "Strategic governance, tier elevation disputes, and sovereign operations."
    })
    channel_map["council-chamber"] = c_ch["id"]

    # Council Boardroom voice channel
    c_vc = api_call(f"/guilds/{GUILD_ID}/channels", method="POST", data={
        "name": "Council Boardroom",
        "type": 2,
        "parent_id": gov_cat_id
    })
    print("Created High Council Governance category & channels.")

# 4. Post Clearance Architecture in #manifesto
if "manifesto" in channel_map:
    matrix_embed = {
        "title": "🏛️ THE CLEARANCE MATRIX // EARNED SOVEREIGNTY PROTOCOL",
        "description": (
            "Clearance in **THE ONE** is strictly meritocratic and earned through verified output.\n\n"
            "---|---|---\n"
            "### `[ III ] Initiate` (The Foyer)\n"
            "• **Permissions:** Restricted text in `#introductions` and `#proof-of-work`. Cannot attach media or view the Enclave.\n"
            "• **Objective:** Submit your background and verifiable proof of work.\n\n"
            "### `[ II ] Syndicate Member` (The Enclave)\n"
            "• **Permissions:** Complete server clearance. Access to `#the-nexus`, `#first-blood`, `#offer-and-pricing`, all Domain Labs, and Voice Bunkers.\n"
            "• **Qualification:** Shipped a verifiable software product, generated first revenue, or closed client contracts.\n\n"
            "### `[ I ] The Council` (Domain Leadership)\n"
            "• **Permissions:** Priority Speaker, moderation authority, access to private `#council-chamber` and executive boardrooms.\n"
            "• **Qualification:** Running a proven 6-to-7 figure enterprise, maintaining an essential open-source framework, or directly generating $10k+ in collective ecosystem referrals.\n\n"
            "### `[ 0 ] Core Architect` (Sovereign Founder)\n"
            "• Absolute administrative control and protocol stewardship."
        ),
        "color": 0x9B59B6,
        "footer": {"text": "All-Signal Hierarchy Protocol // Zero-Trust Governance"}
    }
    api_call(f"/channels/{channel_map['manifesto']}/messages", method="POST", data={"embeds": [matrix_embed]})
    print("Posted Clearance Matrix embed in #manifesto.")

print("\nMatrix configuration finalized!")
