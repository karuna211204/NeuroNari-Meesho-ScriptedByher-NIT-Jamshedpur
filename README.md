# 💡 NeuroNari - Meesho ScriptedByHer | NIT Jamshedpur

This repository contains the LiveKit agent and associated backend components for **NeuroNari**, a personalized **AI Health Assistant** built during the **Meesho ScriptedByHer Hackathon**.

It integrates:

- **LiveKit** for real-time audio/video interaction
- A custom **MCP (Multi-Channel Protocol)** backend
- Tools for multilingual voice processing, appointment management, health records, and notifications

---

## 📌 1. Project Overview

The system architecture includes:

- **`livekit_agent.py`** – Core LiveKit agent that connects to rooms, processes voice streams, and interacts with AI logic.
- **`mcp_server.py` / `mcp_client/`** – Custom MCP server/client system to manage queues, appointments, and tool access.
- **`schemas.py`** – Defines data models and validation schemas.
- **`requirements.txt`** – Python dependencies.

---

## 🧰 2. Prerequisites

Install the following before proceeding:

- [Python 3.9+](https://www.python.org/)
- [Git](https://git-scm.com/)
- [LiveKit Cloud Account](https://cloud.livekit.io/) – Required for creating projects and API credentials

---

## ⚙️ 3. Local Setup Guide

### 📥 3.1 Clone the Repository

```bash
git clone https://github.com/karuna211204/NeuroNari-Meesho-ScriptedByher-NIT-Jamshedpur.git
cd NeuroNari-Meesho-ScriptedByher-NIT-Jamshedpur
```

### 🛠️ 3.2 Set Up a Virtual Environment

```bash
# Create
python -m venv venv

# Activate
# Windows:
.\venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 📦 3.3 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔗 4. LiveKit Cloud Configuration

### 🌐 4.1 Create Project

- Go to [LiveKit Playground](https://cloud.livekit.io/)
- Create a new project (e.g., `Health Assistant AI`)

### 🔑 4.2 Get API Key & Secret

- From your project dashboard, find:

  - `LIVEKIT_API_KEY` → e.g., `DEV_xxxxxx`
  - `LIVEKIT_API_SECRET` → e.g., `SK_xxxxxx`

> ⚠️ **Never share or commit your secret.**

### 📄 4.3 Configure Environment Variables

1. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

2. Fill it like this:

```env
# LiveKit Configuration
LIVEKIT_WS_URL=wss://<YOUR_LIVEKIT_PROJECT_URL>
LIVEKIT_API_KEY=<YOUR_LIVEKIT_API_KEY>
LIVEKIT_API_SECRET=<YOUR_LIVEKIT_API_SECRET>
LIVEKIT_DEBUG_MODE=True

# Google API Key
GOOGLE_API_KEY=<YOUR_GOOGLE_API_KEY>

# Twilio Configuration
TWILIO_FROM_NUMBER=<YOUR_TWILIO_PHONE_NUMBER>
TWILIO_ACCOUNT_SID=<YOUR_TWILIO_ACCOUNT_SID>
TWILIO_AUTH_TOKEN=<YOUR_TWILIO_AUTH_TOKEN>

# MCP Server
MCP_URL=http://127.0.0.1:8000
```

---

## ▶️ 5. Running the Project

### ⚙️ 5.1 Start MCP Server

```bash
# Ensure virtual env is activated
# Start server:
python mcp_server.py
# or (if applicable)
python mcp_client/server.py
```

### 🗣️ 5.2 Start LiveKit Agent

In a **new terminal window**:

```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # macOS/Linux

# Run agent
python livekit_agent.py start
```

---

## 🧪 5.3 Generate Access Token (for Playground)

Create a new file: `generate_token.py`

```python
import os
from dotenv import load_dotenv
from livekit import AccessToken, VideoGrants

load_dotenv()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_WS_URL")

grants = VideoGrants(
    room_join=True,
    room_create=True,
    can_publish=True,
    can_subscribe=True
)

token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
token.add_grants(grants)
token.set_identity("playground-user")
token.set_name("playground-user")
token.set_ttl(3600)

print(f"LiveKit Room URL: {LIVEKIT_URL}")
print(f"Room Name: my-health-assistant-room")
print("JWT Token:")
print(token.to_jwt())
```

Then run:

```bash
python generate_token.py
```

Copy the JWT token for use in [LiveKit Agent Playground](https://playground.livekit.io/).

---

## 🧪 5.4 Test Backend Tools

```bash
python test_queue.py
```

This verifies if queue-based appointment handling via the MCP server is working as well as all other remaining tools.

---

## 📁 6. Project Structure

```
├── .env.example             # Sample environment config
├── .gitignore               # Ignored files list
├── livekit_agent.py         # Main LiveKit AI agent
├── mcp_server.py            # MCP server backend
├── mcp_client/
│   ├── server.py            # MCP client-side server
│   └── mcp_utils.py         # Utility methods
├── schemas.py               # Data models
├── requirements.txt         # Python dependencies
├── test_queue.py            # Tool tester script
├── generate_token.py        # Token generator script
```

---

## 🛠️ 7. Troubleshooting

| Issue                          | Solution                                                               |
| ------------------------------ | ---------------------------------------------------------------------- |
| `ModuleNotFoundError`          | Activate venv and run `pip install -r requirements.txt`                |
| LiveKit connection failure     | Double-check `LIVEKIT_WS_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` |
| Git merge conflict             | Run `git merge --abort` or resolve then `git commit`                   |
| Push rejected                  | Run `git pull origin main --allow-unrelated-histories` then `git push` |
| Playground “Failed to connect” | Ensure token, room name, and agent script match exactly                |

---

## 🤝 8. Contributing

1. Fork the repo
2. Create a feature branch
3. Make changes & commit
4. Push to your branch
5. Open a Pull Request

---

## 📜 9. License

**MIT License**

```
MIT License

Copyright 2025 Karuna Sree

```
