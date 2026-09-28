# ALL-SIGNAL // SYNDICATE CORE ENGINE

[![Security: Zero-Trust](https://img.shields.io/badge/SECURITY-ZERO--TRUST-red?style=for-the-badge)](https://github.com/All-Signal)
[![Infrastructure: Operational](https://img.shields.io/badge/INFRASTRUCTURE-OPERATIONAL-00FF66?style=for-the-badge)](https://github.com/All-Signal)
[![Discord Gateway](https://img.shields.io/badge/DISCORD-ORACLE%20ONLINE-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/nvbbpcedNF)

> *"Chaos is not a disorder to be cured. It is unchanneled compute waiting for an architecture."*

The operational nervous system of **ALL-SIGNAL**. Manages Discord community architecture, clearance gating, autonomous ritual engines, interactive skill trees, and internal bounty markets.

---

## 🏛️ Architecture & Modules

* **`bot.py`**: The live ORACLE background daemon.
  * **Interactive Superpower Skill Tree**: Self-assignable badges (`Growth & Sales`, `Systems & Code`, `Capital & Finance`, `Product & Design`).
  * **One-Click Vetting Engine**: Private queue dispatching proof-of-work review cards with approval buttons for Core Architects.
  * **Weekly Ritual Engine**: Monday 09:00 UTC Sprint Kickoffs & Friday 17:00 UTC Reckoning proof-of-work audits.
  * **Syndicate Commands**:
    * `/post_bounty` — Post tasks, bounties, and rev-share gigs into `#bounties-and-gigs` with auto-generated threads.
    * `/oracle` — 3-mode AI compute engine (concept stress-testing, offer diagnostics, 4-line cold outreach generation).
    * `/promote` & `/demote` — Automated clearance tier management.
* **`deploy.py` & `finish_deploy.py`**: Idempotent server provisioners that configure the full channel taxonomy, categories, and role permissions.
* **`apply_all.py`**: Enforces strict permission gating (hides the syndicate enclave from unverified initiates).
* **`deploy_phase3.py`**: Configures the internal economy, `#bounties-and-gigs`, and permanent gateway invites.

---

## 🚀 Quickstart

### 1. Clone & Setup
```bash
git clone https://github.com/All-Signal/syndicate-core.git
cd syndicate-core
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variables
Copy `.env.example` to `.env` and populate:
```bash
cp .env.example .env
```

```env
APPLICATION_ID=1554102926346027050
CLIENT_ID=1554102926346027050
PUBLIC_KEY=your_public_key
CLIENT_SECRET=your_client_secret
DISCORD_BOT_TOKEN=your_bot_token
GUILD_ID=1554105137855729724
```

### 3. Run Daemon
```bash
python bot.py
```
