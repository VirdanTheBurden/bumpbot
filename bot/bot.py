import nextcord
from loguru import logger
from nextcord.ext import commands

from bot.exts.bumping import Bumping
from bot.exts.threads import Threads
from bot.utils.help import HelpView

bot = commands.Bot()
bot.command_prefix = "%"

bot.add_cog(Threads(bot))
bot.add_cog(Bumping(bot))


TESTING_GUILD_ID = 840691233185988628  # Replace with your guild ID


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")


@bot.slash_command(guild_ids=[TESTING_GUILD_ID])
async def help(interaction: nextcord.Interaction):
    obj = HelpView(bot)
    e = nextcord.Embed.from_dict(obj.get_embed_object(1))
    await interaction.send(view=obj, embed=e, ephemeral=True)


@bot.slash_command(guild_ids=[TESTING_GUILD_ID])
async def reload(interaction: nextcord.Interaction):
    pass
