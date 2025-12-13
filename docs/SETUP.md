# Reachy Mini Discord Bot — Setup Guide

This guide walks you through creating the Discord application, inviting the bot to your server, configuring environment variables, ingesting your knowledge base, and running the bot.

## Prerequisites
- Python 3.10+
- A Discord account and a server where you can add bots (Manage Server permission)
- An OpenAI API key with access to the configured model

## 1) Create the Discord application and bot
1. Open the Discord Developer Portal: https://discord.com/developers/applications
2. Click “New Application”, choose a name (e.g., Reachy Mini), and create it.
3. In the left menu, go to “Bot” and click “Add Bot”. Confirm.
4. Under “Privileged Gateway Intents”, enable:
   - MESSAGE CONTENT INTENT (required for reading messages)
5. Copy the bot Token:
   - Click “Reset Token” (if needed) → “Copy”. Store it securely; you’ll use it as `discord_token`.

## 2) Invite the bot to your server
1. In the left menu, go to “OAuth2” → “URL Generator”.
2. Under Scopes, check:
   - `bot`
   - `applications.commands` (for slash commands like `/ping`)
3. Under Bot Permissions, select at minimum:
   - View Channels
   - Read Message History
   - Send Messages
   - Create Public Threads
   - Create Private Threads
   - Send Messages in Threads
   - Attach Files (optional, improves attachment features)
   - Embed Links (optional)
4. Copy the generated URL and open it in your browser.
5. Select your server and authorize the bot.

Notes
- If messages or threads fail, verify the bot’s role permissions in your server and ensure channel-level overrides allow the above.

## 3) Local environment setup
1. Clone this repository to your machine.
2. Create and activate a virtual environment:
   - `python -m venv .venv && source .venv/bin/activate`
3. Install the package (recommended) or requirements:
   - Recommended: `pip install -U pip && pip install -e .`
   - Alternative: `pip install -U pip && pip install -r requirements.txt`

## 4) Configure environment
1. Create a `.env` file at the project root. You can start from the example:
   - `cp .env.example .env`
2. Fill the following variables:
   - `discord_token` — your bot token from the Developer Portal
   - `OPENAI_API_KEY` — your OpenAI API key
   - Optional overrides:
     - `RAG_DB_PATH` (default `./rag_db`)
     - `RAG_COLLECTION` (default `reachy_mini`)
     - `OPENAI_MODEL` (default `gpt-4o-mini`)
     - `OPENAI_EMBEDDING_MODEL` (default `text-embedding-3-small`)
     - `THREAD_HISTORY_LIMIT` (default `25`) — how many prior messages from the current thread to include in the prompt

Example `.env`
```
discord_token=YOUR_DISCORD_BOT_TOKEN
OPENAI_API_KEY=sk-...
RAG_DB_PATH=./rag_db
RAG_COLLECTION=reachy_mini
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
RAG_DOCUMENTS_PATH=./rag_documents
THREAD_HISTORY_LIMIT=25
```

## 5) Ingest your knowledge base (RAG)
1. Put your documents in a folder (markdown, txt, logs, pdf).
2. Run the ingestion CLI to build the local persistent DB:
   - `reachy-mini-ingest ./my_docs`
3. This creates/updates a local Chroma DB at `RAG_DB_PATH`.

Tips
- Re-run ingestion any time your docs change; it’s idempotent on content chunks.
- Large/complex PDFs are supported via `pdfminer.six` but may parse imperfectly.

## 6) Run the bot
- Start the bot via the installed CLI:
  - `reachy-mini-discord-bot`
- Or run the module directly:
  - `python -m reachy_mini_bot.run`

You should see logs like “Logged in as Reachy Mini (…)”.

## 7) Use the bot in Discord
- Mention the bot in any channel: `@Reachy Mini How do I…?`
- The bot creates a thread (e.g., “Reachy Mini: How do I…”) and replies.
- It will only reply when explicitly @mentioned (even inside that thread).
- Try the slash command `/ping` to verify command registration.
- Use `/add_rag` inside a thread to save its current messages into your RAG documents folder (`RAG_DOCUMENTS_PATH/threads`, default `./rag_documents/threads`). Re-run ingestion on that folder to refresh the RAG DB.
- Attach small text files (`.txt`, `.md`, `.log`) to include them in the context.

## Troubleshooting
- Permissions
  - Ensure the bot role has: View Channels, Read Message History, Send Messages, Create/Send in Threads.
  - Check channel-specific permission overrides if it fails only in certain channels.
- Intents
  - MESSAGE CONTENT INTENT must be enabled in the Developer Portal and your code already enables it.
- Tokens and keys
  - `discord_token` and `OPENAI_API_KEY` must be present in `.env` or environment variables.
- RAG results
  - If nothing is retrieved, the bot still answers but may ask follow-ups. Confirm ingestion ran and `RAG_DB_PATH` points to the DB.
- Slash commands not appearing
  - Command sync can take a minute. Re-invite with `applications.commands` scope if missing.
- Rate limits or long replies
  - The bot splits messages to respect Discord’s 2000-character limit.

## Configuration reference
- `RAG_DB_PATH`: path to Chroma persistent storage (default `./rag_db`).
- `RAG_DOCUMENTS_PATH`: base folder for thread exports saved by `/add_rag` under `threads/` (default `./rag_documents`).
- `RAG_COLLECTION`: collection name (default `reachy_mini`).
- `OPENAI_MODEL`: chat model (default `gpt-4o-mini`).
- `OPENAI_EMBEDDING_MODEL`: embedding model (default `text-embedding-3-small`).

That’s it! If you want help deploying this as a service (e.g., systemd) or containerizing it, let us know.
