import nextcord
from loguru import logger
from nextcord.ext import commands


class Threads(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Threads cog has been fully loaded!")

    @commands.group(invoke_without_command=True)
    async def thread(self, ctx: commands.Context):
        """No use"""

        await ctx.send(
            "This command alone won't do anything. Use /help to figure out what to do!"
        )

    @thread.command()
    async def create(
        self,
        ctx: commands.Context,
        name: str,
        channel: nextcord.channel.TextChannel = None,
        is_public: bool = True,
        duration: int = 1440,
    ):
        """Creates a new (private or public) thread under a provided channel."""

        if channel is None:
            channel = ctx.channel

        if is_public:
            thread_type = nextcord.ChannelType.public_thread
        else:
            thread_type = nextcord.ChannelType.private_thread

            if ctx.guild.premium_tier < 2:
                await ctx.send(
                    "Private threads are only available for Tier 2 servers. Defaulting to public thread."
                )
                thread_type = nextcord.ChannelType.public_thread

        thread = await channel.create_thread(
            name=name, auto_archive_duration=duration, type=thread_type
        )
        logger.info(
            f"Created thread {name} (id: {thread.id}) under channel {channel.name} (id: {channel.id})"
        )

        await thread.add_user(ctx.author)
        logger.info(f"Added user {ctx.author} (id: {ctx.author.id}) to thread {name}")

        await ctx.send(f"Thread {name} has been created under channel {channel.name}")

    @thread.command()
    async def delete(self, ctx: commands.Context, thread: nextcord.Thread):
        """Deletes an arbitrary discord thread."""

        await thread.delete()
        logger.info(
            f"Deleted thread {thread.name} under channel {thread.parent.name} (id: {thread.parent.id})"
        )

        await ctx.send(f"Thread {thread.name} deleted!")

    @thread.command()
    async def archive(self, ctx: commands.Context, thread: nextcord.Thread):
        """Archives an arbitrary discord thread."""

        await thread.edit(archived=True)
        logger.info(
            f"Archived thread {thread.name} under channel {thread.parent.name} (id: {thread.parent.id})"
        )

    @thread.command()
    async def unarchive(self, ctx: commands.Context, thread: nextcord.Thread):
        """Unarchives an arbitrary discord thread."""

        await thread.edit(archived=False)
        logger.info(
            f"Unarchived thread {thread.name} under channel {thread.parent.name} (id: {thread.parent.id})"
        )

    @thread.group(invoke_without_command=True)
    async def edit(self, ctx: commands.Context):
        """No use"""

        await ctx.send(
            "This command alone will not do anything. Use /help to find out what to do!"
        )
