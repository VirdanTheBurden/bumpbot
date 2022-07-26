import nextcord
from loguru import logger
from nextcord.ext import commands


class Threads(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
        channel_id: nextcord.channel.TextChannel = None,
        is_public: bool = True,
        duration: int = 1440,
    ):
        """Creates a new (private or public) thread under a provided channel."""

        if channel_id is None:
            channel_id = ctx.channel

        if is_public:
            thread_type = nextcord.ChannelType.public_thread
        else:
            thread_type = nextcord.ChannelType.private_thread

            if ctx.guild.premium_tier < 2:
                await ctx.send(
                    "Private threads are only available for Tier 2 servers. Defaulting to public thread."
                )
                thread_type = nextcord.ChannelType.public_thread

        thread = await channel_id.create_thread(
            name=name, auto_archive_duration=duration, type=thread_type
        )
        logger.info(
            f"Created thread {name} (id: {thread.id}) under channel {channel_id.name} (id: {channel_id.id})"
        )

        await thread.add_user(ctx.author)
        logger.info(f"Added user {ctx.author} (id: {ctx.author.id}) to thread {name}")

        await ctx.send(
            f'Thread "{name}" has been created under channel {channel_id.name}.'
        )

    @thread.command()
    async def delete(self, ctx: commands.Context, thread_id: nextcord.Thread):
        """Deletes an arbitrary discord thread."""

        await thread_id.delete()
        logger.info(
            f"Deleted thread {thread_id.name} under channel {thread_id.parent.name} (id: {thread_id.parent.id})"
        )

        await ctx.send(f'Thread "{thread_id.name}" deleted!')

    @thread.command()
    async def archive(self, ctx: commands.Context, thread_id: nextcord.Thread):
        """Archives an arbitrary discord thread."""

        await thread_id.edit(archived=True)
        logger.info(
            f"Archived thread {thread_id.name} under channel {thread_id.parent.name} (id: {thread_id.parent.id})"
        )

        await ctx.send(f'Thread "{thread_id.name}" has been archived.')

    @thread.command()
    async def unarchive(self, ctx: commands.Context, thread_id: nextcord.Thread):
        """Unarchives an arbitrary discord thread."""

        await thread_id.edit(archived=False)
        logger.info(
            f"Unarchived thread {thread_id.name} under channel {thread_id.parent.name} (id: {thread_id.parent.id})"
        )

        await ctx.send(f'Thread "{thread_id.name}" is unarchived.')
