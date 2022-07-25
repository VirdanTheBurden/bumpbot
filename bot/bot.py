import json
from pathlib import Path

import nextcord
from loguru import logger
from nextcord.ext import commands

from bot.exts.bumping import Bumping
from bot.exts.threads import Threads
from bot.utils.views import HelpView

bot = commands.Bot()


with open(Path.cwd() / "config.json") as f:
    doc = json.load(f)
    GUILD_ID = doc["guild_id"]
    bot.command_prefix = doc["prefix"]


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")
    bot.add_cog(Threads(bot))
    logger.info("Threads cog has been fully loaded!")
    bot.add_cog(Bumping(bot, GUILD_ID))
    logger.info("Bumping cog has been fully loaded!")


@bot.slash_command(guild_ids=[GUILD_ID])
async def help(interaction: nextcord.Interaction):
    """Provides an embed with all commands and their parameters."""
    obj = HelpView(bot, bot.command_prefix)
    e = nextcord.Embed.from_dict(obj.get_embed_object(1))
    await interaction.send(view=obj, embed=e, ephemeral=True)


@bot.slash_command(guild_ids=[GUILD_ID])
async def shutdown(interaction: nextcord.Interaction):
    """Shuts down Bumpbot gracefully."""

    await interaction.send("Shutting down...")

    bot.remove_cog("Bumping")
    bot.remove_cog("Threads")
    exit()
