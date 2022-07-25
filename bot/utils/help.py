from inspect import Parameter

import nextcord
from nextcord.ext import commands


class HelpView(nextcord.ui.View):
    """Represents the Help embed."""

    def __init__(self, bot):
        super().__init__()
        self._page_number = 1

        # build pages
        self.cog_pages: dict[int, tuple[str, dict]] = {
            k: (v, self._create_page(bot.get_cog(v)))
            for k, v in enumerate(bot.cogs, start=1)
        }

    def _create_page(self, cog: commands.Cog) -> dict:
        """Builds an embed detailing commands out of a cog."""

        embed_object = {
            "title": f'Cog "{cog.qualified_name}"',
            "type": "rich",
            "description": "Registered commands",
            "color": nextcord.Color.yellow().value,
            "fields": [],
        }

        for c in cog.walk_commands():
            if c.help != "No use":
                params = []

                for k, v in c.clean_params.items():
                    if v.default == Parameter.empty:
                        params.append(f"<{k}>")
                    else:
                        params.append(f"<{k}={v.default}>")

                field_object = {
                    "name": f"{c.qualified_name} {' '.join(params)}",
                    "value": c.help,
                    "inline": False,
                }

                embed_object["fields"].append(field_object)

        embed_object["fields"].sort(key=lambda x: x["name"])
        return embed_object

    def get_embed_object(self, page: int) -> dict | None:
        try:
            return self.cog_pages[page][1]
        except KeyError:
            return None

    @nextcord.ui.button(label="Previous Page", style=nextcord.ButtonStyle.blurple)
    async def back(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self._page_number == 1:
            return

        self._page_number = self._page_number - 1
        new_embed = nextcord.Embed.from_dict(self.get_embed_object(self._page_number))
        await interaction.response.edit_message(view=self, embed=new_embed)

    @nextcord.ui.button(label="Next Page", style=nextcord.ButtonStyle.blurple)
    async def forward(
        self, button: nextcord.ui.Button, interaction: nextcord.Interaction
    ):
        if self._page_number == len(self.cog_pages):
            return

        self._page_number = self._page_number + 1
        new_embed = nextcord.Embed.from_dict(self.get_embed_object(self._page_number))
        await interaction.response.edit_message(view=self, embed=new_embed)
