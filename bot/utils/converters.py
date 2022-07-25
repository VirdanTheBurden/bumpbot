import re

from nextcord.ext import commands


class Minutes(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> float:
        minutes: float = 0.0

        time_legend = {"s": 1 / 60, "m": 1, "h": 60, "d": 1440, "w": 10080}

        pattern = re.compile(r"\d+[smhdw]")
        for match in re.finditer(pattern, argument):
            s = match[0]
            minutes += time_legend[s[-1]] * int(s[0:-1])

        return minutes
