import logging
import os
import re
import sys
import traceback
from datetime import datetime
from typing import Any, List, Optional

import aiohttp
import asyncpraw  # type: ignore
import disnake
import yaml
from asyncpraw.models.reddit.submission import Submission  # type: ignore
from asyncpraw.models.reddit.subreddit import Subreddit  # type: ignore
from disnake.ext import tasks
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

with open("./config.yaml", "r", encoding="utf-8") as yamlfile:
    config = yaml.full_load(yamlfile)


LIBRARY_RESOURCES_TRIGGERS: List[str] = config["library_resources"]["triggers"]
HEADCANON_TRIGGERS: List[str] = config["headcanon"]["triggers"]
LIBRARY_RESOURCES: int = config["library_resources"]["id"]
HEADCANON: int = config["headcanon"]["id"]
WAIT_TIME_SECONDS: int = config["wait_time_seconds"]
LIMIT: int = config["limit"]
REQUEST_LIMIT: int = config["request_limit"]


class Bot(commands.Bot):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)  # type: ignore
        self.seen: List[str] = []
        self.current = 0

        self.library_channel: Optional[disnake.TextChannel] = None
        self.headcannon_channel: Optional[disnake.TextChannel] = None

        self.reddit: Optional[asyncpraw.Reddit] = None
        self.subreddit: Optional[Subreddit] = None

        self.loop.create_task(self.once_ready())

    async def once_ready(self):
        await client.wait_until_ready()

        session = aiohttp.ClientSession()
        self.reddit = asyncpraw.Reddit(
            client_id=os.environ["client_id"],
            client_secret=os.environ["client_secret"],
            password=os.environ["password"],
            user_agent=os.environ["user_agent"],
            username=os.environ["reddit_username"],
            requestor_kwargs={"session": session},
        )
        self.subreddit: Optional[Subreddit] = await self.reddit.subreddit("VALORANT")
        await self.subreddit.load()  # type: ignore
        self.library_channel = client.get_channel(LIBRARY_RESOURCES)  # type: ignore
        self.headcannon_channel = client.get_channel(HEADCANON)  # type: ignore

        if not self.library_channel or not self.headcannon_channel:
            logging.fatal("Could not find channel")
            await client.close()
            sys.exit(1)

        self.check_reddit.start()
        logging.info(f"Logged in as {client.user}")

    async def close(self) -> None:
        await self.reddit.close()  # type: ignore
        return await super().close()

    @tasks.loop(seconds=WAIT_TIME_SECONDS, reconnect=True)
    async def check_reddit(self):
        if self.current == LIMIT:
            self.seen.clear()
        self.current += 1

        try:
            async for submission in self.subreddit.new(limit=REQUEST_LIMIT):  # type: ignore
                submission: Submission
                # for each trigger_words
                await self.find_submissions(
                    submission=submission,
                    triggers=LIBRARY_RESOURCES_TRIGGERS,
                    is_for_resources=True,
                    channel=self.library_channel,  # type: ignore
                )
                await self.find_submissions(
                    submission=submission,
                    triggers=HEADCANON_TRIGGERS,
                    is_for_resources=True,
                    channel=self.headcannon_channel,  # type: ignore
                )

        except Exception as error:
            formatted = traceback.format_exception(
                type(error), error, error.__traceback__
            )
            sys.stderr.write(f"\33[91m{''.join(formatted)}\033[0m")
            sys.stderr.flush()

    async def find_submissions(
        self,
        *,
        channel: disnake.TextChannel,
        submission: Submission,
        triggers: List[str],
        is_for_resources: bool = False,
    ):
        if submission.id in self.seen:
            return

        for word in triggers:
            content = f"{submission.title} {submission.selftext}"

            triggered = re.search(rf"\b{word}\b", content, re.IGNORECASE)
            invalid = re.search(
                r"\bagent (concept|idea|suggestion)\b",
                submission.selftext,
                re.IGNORECASE,
            )

            if not triggered or invalid and is_for_resources:
                continue

            await self.send_embed(channel, submission)  # type: ignore
            break

        self.seen.append(submission.id)

    async def send_embed(self, channel: disnake.TextChannel, submission: Submission):
        description = (
            submission.selftext
            if len(submission.selftext) <= 1024
            else f"{submission.selftext[:1020]}..."
        )
        embed = disnake.Embed(
            title=submission.title, description=description, url=submission.url
        )

        await submission.author.load()
        await submission.author.subreddit.load()

        if submission.author.subreddit.over18:
            embed.set_author(
                name=submission.author,
                icon_url=self.subreddit.icon_img,  # type: ignore
            )
        else:
            embed.set_author(
                name=submission.author,
                url=f"https://reddit.com/u/{submission.author}",
                icon_url=submission.author.icon_img,
            )
        embed.timestamp = datetime.utcfromtimestamp(submission.created)

        await channel.send(embed=embed)


client = Bot(
    commands.when_mentioned,
    activity=disnake.Game(name=" alone in a dark place."),
    status=disnake.Status.dnd,
)


if __name__ == "__main__":
    client.remove_command("help")
    client.load_extension("jishaku")
    client.run(os.environ["token"])
