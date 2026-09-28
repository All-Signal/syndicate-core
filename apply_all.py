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

print("========================================")
print("1. RENAME BOT TO 'ORACLE // THE ONE'")
print("========================================")
try:
    api_call("/users/@me", method="PATCH", data={"username": "ORACLE"})
    print("Bot renamed to ORACLE.")
except Exception as e:
    print(f"Note on renaming bot user: {e}")

try:
    api_call(f"/guilds/{GUILD_ID}/members/@me", method="PATCH", data={"nick": "ORACLE // ARCHITECT"})
    print("Server nickname set to 'ORACLE // ARCHITECT'")
except Exception as e:
    print(f"Note on setting nickname: {e}")

print("\n========================================")
print("2. FETCH CHANNELS & ROLES FOR PERMISSION GATING")
print("========================================")
channels = api_call(f"/guilds/{GUILD_ID}/channels")
roles = api_call(f"/guilds/{GUILD_ID}/roles")

role_map = {r["name"]: r["id"] for r in roles}
everyone_role_id = role_map.get("@everyone", GUILD_ID)
syndicate_role_id = role_map.get("[ II ] Syndicate Member")
council_role_id = role_map.get("[ I ] The Council")
architect_role_id = role_map.get("[ 0 ] Core Architect")

VIEW_CHANNEL = 1 << 10
SEND_MESSAGES = 1 << 11
READ_MESSAGE_HISTORY = 1 << 16

# Categories to gate
# Public categories: "📜 // THE PROTOCOL", "🚪 // THE THRESHOLD"
# Private categories (Syndicate Member+): all others
for c in channels:
    if c["type"] == 4: # Category
        cat_name = c["name"]
        cat_id = c["id"]
        
        if "THE PROTOCOL" in cat_name:
            # Everyone can view, but only admins can speak
            overwrites = [
                {
                    "id": everyone_role_id,
                    "type": 0,
                    "allow": str(VIEW_CHANNEL | READ_MESSAGE_HISTORY),
                    "deny": str(SEND_MESSAGES)
                }
            ]
            api_call(f"/channels/{cat_id}", method="PATCH", data={"permission_overwrites": overwrites})
            print(f"Locked category (Read-only for public): {cat_name}")

        elif "THE THRESHOLD" in cat_name:
            # Everyone can view & send intros/proof
            overwrites = [
                {
                    "id": everyone_role_id,
                    "type": 0,
                    "allow": str(VIEW_CHANNEL | SEND_MESSAGES | READ_MESSAGE_HISTORY),
                    "deny": "0"
                }
            ]
            api_call(f"/channels/{cat_id}", method="PATCH", data={"permission_overwrites": overwrites})
            print(f"Opened threshold category: {cat_name}")

        else:
            # Gated Enclave: Hide from @everyone, allow Syndicate Member, Council, Architect
            overwrites = [
                {
                    "id": everyone_role_id,
                    "type": 0,
                    "allow": "0",
                    "deny": str(VIEW_CHANNEL) # Hidden
                }
            ]
            if syndicate_role_id:
                overwrites.append({
                    "id": syndicate_role_id,
                    "type": 0,
                    "allow": str(VIEW_CHANNEL | SEND_MESSAGES | READ_MESSAGE_HISTORY),
                    "deny": "0"
                })
            if council_role_id:
                overwrites.append({
                    "id": council_role_id,
                    "type": 0,
                    "allow": str(VIEW_CHANNEL | SEND_MESSAGES | READ_MESSAGE_HISTORY),
                    "deny": "0"
                })
            if architect_role_id:
                overwrites.append({
                    "id": architect_role_id,
                    "type": 0,
                    "allow": str(VIEW_CHANNEL | SEND_MESSAGES | READ_MESSAGE_HISTORY),
                    "deny": "0"
                })

            api_call(f"/channels/{cat_id}", method="PATCH", data={"permission_overwrites": overwrites})
            print(f"Enclave Gated category: {cat_name}")
        time.sleep(0.4)

channel_map = {c["name"]: c["id"] for c in channels}

print("\n========================================")
print("3. SEEDING #resource-vault WITH MASTER PLAYBOOKS")
print("========================================")
if "resource-vault" in channel_map:
    ch_id = channel_map["resource-vault"]

    # Playbook 1: Asymmetric Cold Outreach Framework
    pb1 = {
        "title": "🗄️ PLAYBOOK 01 // ASYMMETRIC OUTREACH ARCHITECTURE",
        "description": (
            "### The Problem with 99% of Cold Outreach:\n"
            "People pitch solutions to problems prospects haven't acknowledged having, using generic AI fluff.\n\n"
            "### The 4-Line Asymmetric Model:\n"
            "```text\n"
            "Line 1 (Proof of Context): Saw your recent [launch/interview/post on X], specifically how you solved [Specific Detail].\n"
            "Line 2 (Observation / Friction Point): Noticed you're using [Current Tool/Workflow] — have you run into [Specific Asymmetric Bottleneck]?\n"
            "Line 3 (Asymmetric Offer): We engineered a custom module that fixes [Bottleneck] and added [Concrete Result] for [Similar Brand]. Built a 60-second Loom showing exactly where the friction is in your setup.\n"
            "Line 4 (Low-Friction CTA): Mind if I drop the link over? No pitch, just feedback.\n"
            "```\n\n"
            "**Golden Rule:** Never ask for a 30-minute call upfront. Sell the permission to send a 60-second proof of competency."
        ),
        "color": 0x3498DB,
        "footer": {"text": "Vault Resource // Syndicate Exclusive"}
    }
    api_call(f"/channels/{ch_id}/messages", method="POST", data={"embeds": [pb1]})
    time.sleep(0.5)

    # Playbook 2: High-Ticket Offer Diagnostic Matrix
    pb2 = {
        "title": "🗄️ PLAYBOOK 02 // HIGH-TICKET OFFER VALIDATION MATRIX",
        "description": (
            "### Can you charge $5k - $15k/mo retainers for your build?\n"
            "Run your product/agency offer through the 4-part stress test:\n\n"
            "**1. Revenue Distance:**\n"
            "• Bad: 'I design logos.' (Infinite distance to cash)\n"
            "• Elite: 'I redesign landing page checkout funnels for DTC brands doing $1M+ to lift conversions by 1.8%.' (Direct line to cash)\n\n"
            "**2. Urgent Pain vs. Luxury Improvement:**\n"
            "• Is this solving an ongoing bleed (wasted ad spend, manual ops eating 20hrs/week) or an aesthetic upgrade?\n\n"
            "**3. Reversibility / Asymmetry:**\n"
            "• Can you offer a performance guarantee, milestone split, or pilot tranche to de-risk the close?\n\n"
            "**4. Pricing Anchor:**\n"
            "• Price against the alternative (hiring a full-time senior engineer at $160k/yr), not against your hourly labor."
        ),
        "color": 0x2ECC71,
        "footer": {"text": "Vault Resource // Syndicate Exclusive"}
    }
    api_call(f"/channels/{ch_id}/messages", method="POST", data={"embeds": [pb2]})
    time.sleep(0.5)

    # Playbook 3: Joint Venture & Split Agreement Memo
    pb3 = {
        "title": "🗄️ PLAYBOOK 03 // SYNDICATE CO-FOUNDER & JV MEMO",
        "description": (
            "### When Technical Minds Pair With Distribution Minds:\n"
            "Before writing a single line of code together in **#co-founder-and-teams**, execute a 1-page alignment protocol:\n\n"
            "1. **Ownership & IP:** Who owns the base repo if the venture dissolves?\n"
            "2. **The 90-Day Cliff:** No equity or revenue split vests unless both parties deliver their core milestones (e.g. MVP built + first 3 paying clients).\n"
            "3. **Capital Contribution:** 100% of initial software/tooling expenses are split or deducted before profit distribution.\n"
            "4. **Severability:** Clean buyout clauses defined upfront when emotions are calm."
        ),
        "color": 0xE67E22,
        "footer": {"text": "Vault Resource // Syndicate Exclusive"}
    }
    api_call(f"/channels/{ch_id}/messages", method="POST", data={"embeds": [pb3]})
    time.sleep(0.5)
    print("Seeded playbooks into #resource-vault.")

print("\n========================================")
print("4. PINNING 'FIRST 5 CLIENTS' PLAYBOOK IN #first-blood")
print("========================================")
if "first-blood" in channel_map:
    fb_id = channel_map["first-blood"]
    guide_embed = {
        "title": "⚡ THE FIRST 5 CLIENTS // THE SPRINT BLUEPRINT",
        "description": (
            "Getting your first client is psychological warfare with yourself. Here is the exact playbook:\n\n"
            "### Phase 1: The 'Warm Tapestry' Audit\n"
            "• Do not blast cold strangers first. List 25 people you've worked with, studied with, or spoken to in the last 2 years.\n"
            "• Message: *“Hey [Name], launching a new high-leverage [AI automation/growth engine] for [Industry]. Looking for 2 beta case studies to run it completely cost-free in exchange for a ruthless video testimonial. Know anyone dealing with [Pain Point]?”*\n\n"
            "### Phase 2: The Value-First Trojan Horse\n"
            "• Find 10 target companies. Find their biggest public inefficiency.\n"
            "• Build a partial fix (a working script, a redesigned hero section, an audit report).\n"
            "• Send it unprompted: *“Built this for you this morning. Use it freely. If you want the full architecture deployed, let's talk.”*\n\n"
            "### Phase 3: The Syndicate Network\n"
            "• Post your offer in **#offer-and-pricing** for review.\n"
            "• Look in **#client-referrals** for overflow leads passed by other members."
        ),
        "color": 0xF1C40F,
        "footer": {"text": "Pinned Masterclass // First Blood"}
    }
    msg = api_call(f"/channels/{fb_id}/messages", method="POST", data={"embeds": [guide_embed]})
    # Pin message
    msg_id = msg["id"]
    api_call(f"/channels/{fb_id}/pins/{msg_id}", method="PUT")
    print("Pinned First 5 Clients guide in #first-blood.")

print("\nAll setup complete!")
