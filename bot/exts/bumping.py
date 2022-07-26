import datetime
import json
from pathlib import Path
from typing import TextIO

import nextcord
from loguru import logger
from nextcord.ext import commands, tasks

from ..utils.converters import Minutes


class Bumping(commands.Cog):
    def __init__(self, bot: commands.Bot, guild_id: int):
        self.bot = bot
        self._GUILD_ID = guild_id

        self._scheduled_threads: dict[
            int, tuple[tasks.Loop, datetime.datetime, str, int]
        ] = {}

        try:
            with open(Path.cwd() / "thread_schedule.json", "r+") as f:
                if len(f.readlines()) != 0:
                    f.seek(0)
                    self._deserialize(f)
        except FileNotFoundError:
            logger.warning("thread_schedule.json does not exist, skipping...")
            

    def _serialize(self):
        """Saves state of scheduled threads."""

        with open(Path.cwd() / "thread_schedule.json", "w") as f:

            to_serialize = {}

            for id, v in self._scheduled_threads.items():

                v[0].cancel()

                data = {
                    "creation_date": v[1].isoformat(),
                    "next_iteration": v[0].next_iteration.isoformat(),
                    "interval": v[0].minutes,
                    "message": v[2],
                }

                to_serialize[id] = data

            json.dump(to_serialize, f)

    def _deserialize(self, file: TextIO):
        """Loads state of scheduled threads and starts them."""

        scheduled_tasks: dict[int, tuple[tasks.Loop, datetime.datetime, str]] = {}

        for id, data in json.load(file).items():
            task = self._build_task(int(id), data["interval"], data["message"])
            scheduled_tasks[int(id)] = (
                task,
                datetime.datetime.fromisoformat(data["creation_date"]),
                data["message"],
                data["interval"],
            )

            scheduled_tasks[int(id)][0].start()

        file.truncate(0)
        self._scheduled_threads = scheduled_tasks

    def _build_task(
        self, thread_id: nextcord.Thread | int, interval: int, message: str
    ) -> tasks.Loop:
        """Builds a thread bump task."""

        if not isinstance(thread_id, nextcord.Thread):
            for thread in self.bot.get_guild(self._GUILD_ID).threads:
                if thread.id == thread_id:
                    thread_id = thread
                    break

        @tasks.loop(minutes=interval)
        async def f():
            await thread_id.send(message)

        return f

    def cog_unload(self) -> None:
        logger.info("Unloading...")
        self._serialize()

    @commands.group(invoke_without_command=True)
    async def bump(
        self,
        ctx: commands.Context,
        thread_id: nextcord.Thread,
        message: str = "Bump!",
        delete_after: bool = False,
        *,
        silent: bool = False,
    ):
        """Sends a message to an arbitrary discord thread."""

        msg: nextcord.Message = await thread_id.send(message)
        logger.info(f"Bumped {thread_id.name} (id: {thread_id.id})")

        if not silent:
            await ctx.send(f"Thread {thread_id.name} bumped!")

        if delete_after:
            await msg.delete()

    @bump.command()
    async def schedule(
        self,
        ctx: commands.Context,
        thread_id: nextcord.Thread,
        interval: Minutes,
        message: str = "Bump!",
    ):
        """Sends a message to an arbitrary discord thread in a regular interval."""

        if interval > thread_id.auto_archive_duration:
            await ctx.send(
                "The interval time is larger than the auto archive time. Provide a shorter interval."
            )
            return

        task = self._build_task(thread_id, interval, message)

        self._scheduled_threads[thread_id.id] = (
            task,
            datetime.datetime.now(tz=datetime.timezone.utc),
            message,
        )

        task.start()
        await ctx.send(
            f"Thread {thread_id.name} will be bumped every {interval} minutes."
        )
        logger.info(
            f"Started new bump task on thread {thread_id.name} (id: {thread_id.id})"
        )

    @bump.command()
    async def unschedule(self, ctx: commands.Context, thread_id: nextcord.Thread):
        """Removes a thread from being bumped further."""

        task_object: tasks.Loop = self._scheduled_threads.get(thread_id.id, None)[0]

        if task_object is None:
            await ctx.send(f"Thread {thread_id.name} is not scheduled for bumping.")
            return

        task_object.cancel()
        logger.info(f"Removed task for thread {thread_id.name} (id: {thread_id.id})")

    @bump.command()
    async def status(self, ctx: commands.Context, thread_id: nextcord.Thread = None):
        """Displays the scheduling status of a thread."""

        if thread_id is None:
            embeds: list[nextcord.Embed] = []
            threads: list[nextcord.Thread] = [
                thread
                for thread in self.bot.get_guild(self._GUILD_ID).threads
                if thread.id in self._scheduled_threads
            ]


            for thread in threads:

                format_str = r"%b %d %Y %H:%M:%S %Z"
                utc_time: datetime.datetime = self._scheduled_threads[thread.id][
                    0
                ].next_iteration.astimezone(tz=datetime.timezone.utc)
                next_bump: str = utc_time.strftime(format_str)
                creation_date = self._scheduled_threads[thread.id][1].strftime(
                    format_str
                )

                embed: nextcord.Embed = nextcord.Embed()
                embed.title = f"Status of thread {thread.name}"
                embed.color = nextcord.Color.green()
                embed.add_field(name="Scheduled", value="true", inline=False)
                embed.add_field(name="Next bump", value=next_bump, inline=False)
                embed.add_field(
                    name="Bump task created at", value=creation_date, inline=False
                )
                embed.add_field(
                    name="Interval",
                    value=f"{self._scheduled_threads[thread.id][0].minutes} minutes",
                    inline=False,
                )

                embeds.append(embed)
            
            await ctx.send(embeds=embeds)
            return


        embed: nextcord.Embed = nextcord.Embed()
        embed.title = f"Status of thread {thread_id.name}"

        if thread_id.id not in self._scheduled_threads:
            embed.color = nextcord.Color.red()
            embed.add_field(name="Scheduled", value="false", inline=False)
            embed.add_field(name="Next bump", value="N/A", inline=False)
            embed.add_field(name="Bump task created at", value="N/A", inline=False)
            embed.add_field(name="Interval", value="N/A", inline=False)

        else:
            format_str = r"%b %d %Y %H:%M:%S %Z"
            utc_time: datetime.datetime = self._scheduled_threads[thread_id.id][
                0
            ].next_iteration.astimezone(tz=datetime.timezone.utc)
            next_bump: str = utc_time.strftime(format_str)
            creation_date = self._scheduled_threads[thread_id.id][1].strftime(
                format_str
            )

            embed.color = nextcord.Color.green()
            embed.add_field(name="Scheduled", value="true", inline=False)
            embed.add_field(name="Next bump", value=next_bump, inline=False)
            embed.add_field(
                name="Bump task created at", value=creation_date, inline=False
            )
            embed.add_field(
                name="Interval",
                value=f"{self._scheduled_threads[thread_id.id][0].minutes} minutes",
                inline=False,
            )

        await ctx.send(embed=embed)
