from nextcord.ext import tasks, commands
import nextcord
from loguru import logger
import datetime
from ..utils.converters import Minutes


class Bumping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._scheduled_threads: dict[int, tuple(tasks.Loop, datetime.datetime)] = {}
    

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Bumping cog has been fully loaded!")


    @commands.group(invoke_without_command=True)
    async def bump(self, ctx: commands.Context, thread: nextcord.Thread, message: str = "Bump!", *, silent: bool = False):
        """Sends a message to an arbitrary discord thread."""

        await thread.send(message)
        logger.info(f"Bumped {thread.name} (id: {thread.id})")

        if not silent:
            await ctx.send(f"Thread {thread.name} bumped!")
    

    @bump.command()
    async def schedule(self, ctx: commands.Context, thread: nextcord.Thread, interval: Minutes, message: str = "Bump!"):
        """Sends a message to an arbitrary discord thread in a regular interval."""

        if interval > thread.auto_archive_duration:
            await ctx.send("The interval time is larger than the auto archive time. Provide a shorter interval.")
            return

        @tasks.loop(minutes=interval)
        async def task():
            await self.bump(ctx, thread, message, silent=True)

        self._scheduled_threads[thread.id] = (task, datetime.datetime.now(tz=datetime.timezone.utc))

        task.start()
        await ctx.send(f"Thread {thread.name} will be bumped every {interval} minutes.")
        logger.info(f"Started new bump task on thread {thread.name} (id: {thread.id})")


    @bump.command()
    async def unschedule(self, ctx: commands.Context, thread: nextcord.Thread):
        """Removes a thread from being bumped further."""

        task_object: tasks.Loop = self._scheduled_threads.get(thread.id, None)

        if task_object is None:
            await ctx.send(f"Thread {thread.name} is not scheduled for bumping.")
            return
        
        task_object.cancel()
        logger.info(f"Removed task for thread {thread.name} (id: {thread.id})")
    

    @bump.command()
    async def status(self, ctx: commands.Context, thread: nextcord.Thread):
        """Displays the scheduling status of a thread."""
        
        embed: nextcord.Embed = nextcord.Embed()
        embed.title = f"Status of thread {thread.name}"

        if thread.id not in self._scheduled_threads:
            embed.color = nextcord.Color.red()
            embed.add_field(name="Scheduled", value="false", inline=False)
            embed.add_field(name="Next bump", value="N/A", inline=False)
            embed.add_field(name="Bump task created at", value="N/A", inline=False)
        
        else:
            format_str = r"%b %d %Y %H:%M:%S %Z"
            utc_time: datetime.datetime = self._scheduled_threads[thread.id][0].next_iteration.astimezone(tz=datetime.timezone.utc)
            next_bump: str = utc_time.strftime(format_str)
            creation_date = self._scheduled_threads[thread.id][1].strftime(format_str)

            embed.color = nextcord.Color.green()
            embed.add_field(name="Scheduled", value="true", inline=False)
            embed.add_field(name="Next bump", value=next_bump, inline=False)
            embed.add_field(name="Bump task created at", value=creation_date, inline=False)
        
        await ctx.send(embed=embed)

