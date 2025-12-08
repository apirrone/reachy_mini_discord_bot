# Reachy Mini Discord Bot (RAG + OpenAI)

A Discord bot named "Reachy Mini" that creates a thread for every conversation and answers using a local RAG database augmented with OpenAI models.

## Features
- Mention the bot anywhere (e.g., `@Reachy Mini ...`) and it creates a thread.
- Continues the conversation inside that thread.
- RAG retrieval from a local persistent DB (Chroma) with OpenAI embeddings.
- Simple ingestion CLI to index your docs/logs.

## Setup
For a complete, step-by-step guide (Discord application, invite, env, ingestion, run), see:

- `docs/SETUP.md`

Quick start:
1. Python 3.10+
2. Create a Discord application + bot, invite it with `MESSAGE CONTENT INTENT` enabled.
3. Create a virtualenv and install (package or requirements):
   - `python -m venv .venv && source .venv/bin/activate`
   - EITHER `pip install -U pip && pip install -e .` (recommended)
   - OR `pip install -U pip && pip install -r requirements.txt`
4. Configure environment:
   - Copy `.env.example` to `.env` and fill `discord_token` and `OPENAI_API_KEY`.

## Ingest your knowledge base
Put your documents (markdown, txt, logs, pdf) in a folder, then run:

CLI (after install): `reachy-mini-ingest ./my_docs`

This builds a local persistent DB at `RAG_DB_PATH` (default `./rag_db`). Re-run when your docs change; it's idempotent.

## Run the bot
CLI (after install): `reachy-mini`

Then in any channel, mention the bot:
```
@Reachy Mini Hi! I have a connection error with my robot... here are some logs
```
A thread is created and the bot replies using RAG + OpenAI.

## Notes
- The bot only replies in threads it creates or when @mentioned in a channel.
- Large answers are split to respect Discord's 2000-char limit.
- Attachments with text content (e.g., `.txt`, `.log`, `.md`) are read and added to context when small enough.

## Configuration
- `RAG_DB_PATH`: path to Chroma persistent storage.
- `RAG_COLLECTION`: collection name (default: `reachy_mini`).
- `OPENAI_MODEL`: chat model (default: `gpt-4o-mini`).
- `OPENAI_EMBEDDING_MODEL`: embedding model (default: `text-embedding-3-small`).

## Project layout
- `reachy_mini_bot/discord_bot.py` — Discord client and thread handling
- `reachy_mini_bot/rag.py` — RAG storage and retrieval helpers
- `reachy_mini_bot/openai_client.py` — OpenAI chat/embedding helpers
- `reachy_mini_bot/scripts/ingest.py` — CLI to index a folder of docs
- `reachy_mini_bot/run.py` — small entrypoint to launch the bot

## Safety & behavior
- Answers include retrieved context summaries when helpful; if unsure, the bot asks clarifying questions.
- The bot avoids fabricating steps and cites document titles/paths when possible.

## Troubleshooting
- Ensure the bot has `MESSAGE CONTENT INTENT` enabled in the Discord Developer Portal and in code.
- If RAG returns no results, the bot will still answer but may ask for more details.
- For PDF ingestion, `pdfminer.six` is used; complex PDFs may parse imperfectly.
