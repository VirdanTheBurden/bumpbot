from dotenv import dotenv_values

from bot.bot import bot

bot.run(dotenv_values(".env")["TOKEN"])
