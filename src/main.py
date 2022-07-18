import nextcord
from nextcord.ext import commands
from dotenv import dotenv_values

TESTING_GUILD_ID = 870126657766301697  # Replace with your guild ID

bot = commands.Bot()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command(description="My first slash command", guild_ids=[TESTING_GUILD_ID])
async def hello(interaction: nextcord.Interaction):
    await interaction.send("Hello!")

bot.run(dotenv_values(".env")["TOKEN"])