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
                retry_after = err_json.get("retry_after", 1.0)
                print(f"[Rate limit] sleeping {retry_after}s...")
                time.sleep(retry_after)
                continue
            else:
                print(f"HTTPError {e.code} on {method} {path}: {err_body}")
                raise e

print("1. Fetching guild data...")
channels = api_call(f"/guilds/{GUILD_ID}/channels")
roles = api_call(f"/guilds/{GUILD_ID}/roles")

channel_map = {c["name"]: c["id"] for c in channels}
role_map = {r["name"]: r["id"] for r in roles}

syndicate_cat_id = None
threshold_cat_id = None
for c in channels:
    if c["type"] == 4:
        if "SYNDICATE COLLABORATION" in c["name"]:
            syndicate_cat_id = c["id"]
        elif "THE THRESHOLD" in c["name"]:
            threshold_cat_id = c["id"]

# 1. Create #bounties-and-gigs channel
if "bounties-and-gigs" not in channel_map and syndicate_cat_id:
    payload = {
        "name": "bounties-and-gigs",
        "type": 0,
        "parent_id": syndicate_cat_id,
        "topic": "Internal paid work, contract tasks, and revenue-share bounties between members."
    }
    ch = api_call(f"/guilds/{GUILD_ID}/channels", method="POST", data=payload)
    channel_map["bounties-and-gigs"] = ch["id"]
    print("Created channel: #bounties-and-gigs")

    # Post template embed in bounties
    bounty_embed = {
        "title": "💰 THE BOUNTY ENGINE // INTERNAL ECONOMY",
        "description": (
            "Post paid gigs, fast contracts, or rev-share opportunities using this format:\n\n"
            "```yaml\n"
            "Deliverable: [e.g. Next.js landing page / Python scraper / Cold email list]\n"
            "Compensation: [$500 cash / 15% rev-share / trade: automation script]\n"
            "Turnaround: [e.g. 48 hours / 1 week]\n"
            "Requirements: [Stack, expectations, proof needed]\n"
            "Contact: [DM or reply to thread]\n"
            "```\n\n"
            "*Syndicate rule: Pay promptly on delivery. Zero tolerance for delinquent compensation.*"
        ),
        "color": 0x2ECC71,
        "footer": {"text": "Syndicate Market"}
    }
    api_call(f"/channels/{ch['id']}/messages", method="POST", data={"embeds": [bounty_embed]})

# 2. Create a permanent Invite Link
manifesto_id = channel_map.get("manifesto")
if manifesto_id:
    try:
        inv_payload = {
            "max_age": 0, # Never expires
            "max_uses": 0, # Unlimited uses
            "unique": False
        }
        invite = api_call(f"/channels/{manifesto_id}/invites", method="POST", data=inv_payload)
        print(f"\n✅ Permanent Invite Code Generated: https://discord.gg/{invite['code']}")
    except Exception as e:
        print(f"Could not generate invite: {e}")

# 3. Create #syndicate-vetting channel for Core Architects
if "syndicate-vetting" not in channel_map and threshold_cat_id:
    everyone_role_id = role_map.get("@everyone", GUILD_ID)
    architect_role_id = role_map.get("[ 0 ] Core Architect")
    council_role_id = role_map.get("[ I ] The Council")

    VIEW_CHANNEL = 1 << 10
    SEND_MESSAGES = 1 << 11
    READ_HISTORY = 1 << 16

    overwrites = [
        {"id": everyone_role_id, "type": 0, "allow": "0", "deny": str(VIEW_CHANNEL)}
    ]
    if architect_role_id:
        overwrites.append({"id": architect_role_id, "type": 0, "allow": str(VIEW_CHANNEL | SEND_MESSAGES | READ_HISTORY), "deny": "0"})
    if council_role_id:
        overwrites.append({"id": council_role_id, "type": 0, "allow": str(VIEW_CHANNEL | SEND_MESSAGES | READ_HISTORY), "deny": "0"})

    v_payload = {
        "name": "syndicate-vetting",
        "type": 0,
        "parent_id": threshold_cat_id,
        "topic": "Private queue where proofs of work are vetted and approved.",
        "permission_overwrites": overwrites
    }
    vch = api_call(f"/guilds/{GUILD_ID}/channels", method="POST", data=v_payload)
    channel_map["syndicate-vetting"] = vch["id"]
    print("Created private channel: #syndicate-vetting")

    queue_embed = {
        "title": "🛡️ VETTING DISPATCH // INITIATE PROOF-OF-WORK QUEUE",
        "description": (
            "When applicants post in **#proof-of-work**, review cards will appear here.\n"
            "You can elevate them with one click or via `/promote`."
        ),
        "color": 0x9B59B6
    }
    api_call(f"/channels/{vch['id']}/messages", method="POST", data={"embeds": [queue_embed]})

print("\nPhase 3 server structure updated successfully!")
