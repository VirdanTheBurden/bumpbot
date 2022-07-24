from tkinter import PAGES
from discord import Color
from dotenv import dotenv_values
from loguru import logger
import nextcord
from nextcord.ext import commands
from exts.bumping import Bumping
from exts.threads import Threads


bot = commands.Bot()
bot.command_prefix = "%"

bot.add_cog(Bumping(bot))
bot.add_cog(Threads(bot))


class HelpView(nextcord.ui.View):
    """Represents the Help embed."""

    def __init__(self):
        self._page_number = 1
        
        # build pages
        self.cog_pages: dict[int, tuple[str, dict]] = {k: (v[0], self._create_page(v[1])) for k, v in enumerate(bot.cogs, start=1)}
        logger.debug(f"built pages: {self.cog_pages}")
    
    def _create_page(self, cog: commands.Cog) -> dict:
        """Builds an embed detailing commands out of a cog."""
        
        embed_object = {
            "title" : f"Cog {cog.qualified_name}",
            "type" : "rich",
            "description" : "Registered commands",
            "color" : nextcord.Color.yellow(),
            "fields" : []
        }

        for c in cog.walk_commands():
            logger.debug(f"command/group found: {c.qualified_name}")

        return embed_object

    def get_embed_object(self, page: int):
        try:
            return self.cog_pages[page][1]
        except KeyError:
            return None
        
    @nextcord.ui.button(label="Back", style=nextcord.ButtonStyle.blurple)
    async def back(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass

    @nextcord.ui.button(label="Forward", style=nextcord.ButtonStyle.blurple)
    async def forward(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass


TESTING_GUILD_ID = 840691233185988628  # Replace with your guild ID


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")

@bot.slash_command(guild_ids=[TESTING_GUILD_ID])
async def help(interaction: nextcord.Interaction):
    obj = HelpView()
    await interaction.send("test embed", view=obj, embed=obj.get_embed_object(1))

@bot.slash_command(guild_ids=[TESTING_GUILD_ID])
async def reload(interaction: nextcord.Interaction):
    pass

bot.run(dotenv_values(".env")["TOKEN"])
