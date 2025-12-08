from __future__ import annotations

import asyncio
import logging
import re
from typing import List, Optional

import discord
from discord import app_commands

from .config import load_settings
from .openai_client import OpenAIClient
from .rag import RAGStore


logger = logging.getLogger("reachy-mini")


class ReachyMiniClient(discord.Client):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True
        super().__init__(*args, intents=intents, **kwargs)

        self.settings = load_settings()
        self.ai = OpenAIClient(self.settings.openai_api_key, self.settings.openai_model)
        self.rag = RAGStore(
            path=self.settings.rag_db_path,
            collection=self.settings.rag_collection,
            openai_api_key=self.settings.openai_api_key,
            embedding_model=self.settings.openai_embedding_model,
        )
        self._sema = asyncio.Semaphore(3)

    async def setup_hook(self) -> None:
        logger.info("Reachy Mini bot is initializing...")
        # Create and sync the app command tree for slash commands
        try:
            self.tree = app_commands.CommandTree(self)
        except Exception:
            # If already present via base class, reuse
            self.tree = getattr(self, "tree", app_commands.CommandTree(self))
        # Add commands (e.g., /ping)
        try:
            self.tree.add_command(ping)
        except Exception:
            pass
        try:
            await self.tree.sync()
        except Exception as e:
            logger.warning("Could not sync app commands: %s", e)

    async def on_ready(self):
        logger.info("Logged in as %s (%s)", self.user, getattr(self.user, "id", "?"))

    async def on_message(self, message: discord.Message):
        # Ignore our own messages and other bots
        if message.author.bot:
            return

        # Only operate in guild contexts
        if not message.guild:
            return

        mentioned = self._is_mentioning_me(message)
        # Reply only when explicitly mentioned, even inside our own threads
        if not mentioned:
            return

        # Ensure we are in a thread; if not, create one from this message
        thread: Optional[discord.Thread]
        if isinstance(message.channel, discord.Thread):
            thread = message.channel
        else:
            thread_name = self._make_thread_name(message)
            try:
                thread = await message.create_thread(name=thread_name, auto_archive_duration=60)
            except discord.Forbidden:
                await message.reply("I don't have permission to create threads here.")
                return
            except discord.HTTPException:
                # Fallback: reply inline if thread cannot be created
                thread = None

        async with self._sema:
            try:
                await self._handle_query(message, thread)
            except Exception as e:
                logger.exception("Error handling message: %s", e)
                try:
                    if thread:
                        await thread.send("Sorry, I hit an error processing that.")
                    else:
                        await message.reply("Sorry, I hit an error processing that.")
                except Exception:
                    pass

    def _is_mentioning_me(self, message: discord.Message) -> bool:
        if not self.user:
            return False
        if self.user in message.mentions:
            return True
        # Also handle raw mention string
        return f"<@{self.user.id}>" in message.content or f"<@!{self.user.id}>" in message.content

    async def _is_in_our_thread(self, message: discord.Message) -> bool:
        ch = message.channel
        if isinstance(ch, discord.Thread):
            # If the thread was created by the bot or has our prefix, we consider it ours
            try:
                if ch.owner_id == self.user.id:
                    return True
            except Exception:
                pass
            return ch.name.startswith("Reachy Mini:")
        return False

    def _make_thread_name(self, message: discord.Message) -> str:
        content = self._strip_mention(message)
        content = re.sub(r"\s+", " ", content).strip()
        if not content:
            content = "Conversation"
        if len(content) > 48:
            content = content[:48] + "…"
        return f"Reachy Mini: {content}"

    def _strip_mention(self, message: discord.Message) -> str:
        content = message.content
        if self.user:
            content = content.replace(f"<@{self.user.id}>", " ")
            content = content.replace(f"<@!{self.user.id}>", " ")
        return content

    async def _collect_text_attachments(self, message: discord.Message, limit_bytes: int = 1_000_000) -> List[str]:
        texts: List[str] = []
        for a in message.attachments:
            name = (a.filename or "").lower()
            if any(name.endswith(ext) for ext in (".txt", ".log", ".md")) or (a.content_type and a.content_type.startswith("text/")):
                if a.size and a.size > limit_bytes:
                    continue
                try:
                    data = await a.read()
                    if data and len(data) <= limit_bytes:
                        texts.append(data.decode("utf-8", errors="replace"))
                except Exception:
                    continue
        return texts

    async def _handle_query(self, message: discord.Message, thread: Optional[discord.Thread]):
        # Show typing indicator while we think/retrieve/respond
        target_channel: discord.abc.Messageable = thread or message.channel
        async with target_channel.typing():
            # Prepare user query text
            user_text = self._strip_mention(message).strip()
            attach_texts = await self._collect_text_attachments(message)
            if attach_texts:
                user_text += "\n\n[Attachments]\n" + "\n\n".join(attach_texts)

            # Retrieve top-k docs
            retrieved = self.rag.query(user_text, k=5)

            # Build prompt
            system_prompt = (
                "You are Reachy Mini, a helpful assistant for troubleshooting robots in a Discord server. "
                "Always respond in English. Be concise and actionable, ask for clarification when needed, and avoid fabricating facts. "
                "Prefer bulleted steps. If you use retrieved context, cite the source filenames or titles in parentheses."
            )

            ctx_parts: List[str] = []
            for d in retrieved:
                src = d.source or d.doc_id
                ctx_parts.append(f"[Source: {src}]\n{d.text}")
            ctx_text = "\n\n".join(ctx_parts) if ctx_parts else "(no context found)"

            # Optionally include a brief thread history (most recent 8 messages)
            history_snippets: List[str] = []
            if isinstance(message.channel, discord.Thread):
                try:
                    async for m in message.channel.history(limit=8, oldest_first=False):
                        role = "assistant" if m.author.bot else "user"
                        content = m.content
                        if content:
                            history_snippets.append(f"{role}: {content}")
                except Exception:
                    pass
            history_text = "\n".join(reversed(history_snippets)) if history_snippets else ""

            user_prompt = (
                f"User message:\n{user_text}\n\n"
                f"Thread history (latest first):\n{history_text}\n\n"
                f"Retrieved context:\n{ctx_text}\n\n"
                "Answer as Reachy Mini."
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            reply = self.ai.chat(messages, temperature=0.2)

        if thread:
            await self._send_long(thread, reply)
        else:
            await self._send_long(message.channel, reply, reference=message)

    async def _send_long(self, channel: discord.abc.Messageable, text: str, reference: Optional[discord.Message] = None):
        # Discord hard limit ~2000 chars per message
        limit = 1900
        chunks: List[str] = []
        t = text or "(no content)"
        while t:
            chunks.append(t[:limit])
            t = t[limit:]
        for i, chunk in enumerate(chunks):
            if i == 0 and reference is not None:
                await channel.send(chunk, reference=reference)
            else:
                await channel.send(chunk)


def run_bot():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    client = ReachyMiniClient()
    client.run(client.settings.discord_token)


@app_commands.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    # Respond quickly; ephemeral keeps channels clean
    await interaction.response.send_message("Pong!", ephemeral=True)
