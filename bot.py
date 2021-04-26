import praw
import discord
import re
import datetime

from discord.ext import tasks
from random import randint
from datetime import datetime

# REDDIT INITILISATION

reddit = praw.Reddit(client_id='CHECK-PRAW-TUTORIALS', \
                     client_secret='CHECK-PRAW-TUTORIALS', \
                     password='REDDIT-ACCOUNT-PSWD',
                     user_agent='CHECK-PRAW-TUTORIALS',
                     username="REDDIT-ACCOUNT-USRNAME")

# which subreddit to scrap
subreddit = reddit.subreddit("VALORANT")

# trigger words for the library-ressources
trigger_words = {
    "lore",
    "backstory",
    "origin",
    "narrative",
    "storyline",
    "protocol",
    "kingdom",
    "plot"
}

# trigger words for the headcanon
trigger_words_hdcn = {
    "agent concept",
    "agent suggestion",
    "agent idea",
    "map concept",
    "map idea",
    "character idea",
    "character concept",
    "agent name"
}

agent_base = "http://www.shiick.xyz/VALORANT/TX_Character_Thumb_"

timestamp = 0

agents = [
    "Breach.png",
    "Guide.png",
    "Gumshoe.png",
    "Hunter.png",
    "Killjoy.png",
    "Pandemic.png",
    "Phoenix.png",
    "Raze.png",
    "Rift.png",
    "Sarge.png",
    "Stealth.png",
    "Thorne.png",
    "Vampire.png",
    "Wraith.png",
    "Wushu.png"
]

# agent colors, in order
agent_colors = [0x5e4032, 0x614434, 0x504c4a, 0x7b7169, 0x565135, 0x343135, 0x483730, 0x5e4638, 0x3a2b31, 0x573927, 0x33334c, 0x524844, 0x49343d, 0x363e6b, 0x756d74]

no_repost = []
current = 0

limit = 720

req_limit = 50

#######################

# DISCORD INITILISATION

client = discord.Client()
channel_id = 753711214663696485 # library ressource id
channel_id_hd = 751586338846933105 # headcanon id
WAIT_TIME_SECONDS = 300

#######################

# DISCORD EVENTS

@client.event
async def on_ready():
    # initiate values
    global channel, channelHC
    # initiate library-ressource
    channel = client.get_channel(channel_id)
    # initiate headcanon
    channelHC = client.get_channel(channel_id_hd)
    # start coroutine for checking reddit
    check_reddit.start()
    # logging the bot name
    print('We have logged in as {0.user}'.format(client))
    # change bot presence
    await client.change_presence(activity=discord.Game(name=" alone in a dark place."), status=discord.Status.online)

@tasks.loop(seconds=WAIT_TIME_SECONDS)
async def check_reddit():
    # initiate values
    new_timestamp = 0
    posted = []
    global current
    global no_repost
    # clearing if the bot can clear his memory
    if (current == limit):
        # clear memory
        no_repost.clear()
    # adding 1 to the current time check
    current = current + 1
    global timestamp
    try:
        # for each new submissions in the req_limit
        for submission in subreddit.new(limit=req_limit):
            # for each trigger_words
            for word in trigger_words:
                # if it's not a repost
                if (submission.created > timestamp and submission.id not in posted and submission.id not in no_repost):
                    # regex bullshit :clown:
                    title = re.search("\\b" + word + "\\b", submission.title.lower())
                    content = re.search("\\b" + word + "\\b", submission.selftext.lower())
                    conceptT = re.search("\\b" + "agent concept" + "\\b", submission.selftext.lower())
                    conceptC = re.search("\\b" + "agent concept" + "\\b", submission.title.lower())
                    concept2T = re.search("\\b" + "agent idea" + "\\b", submission.selftext.lower())
                    concept2C = re.search("\\b" + "agent idea" + "\\b", submission.title.lower())
                    concept3T = re.search("\\b" + "agent suggestion" + "\\b", submission.selftext.lower())
                    concept3C = re.search("\\b" + "agent suggestion" + "\\b", submission.title.lower())
                    # if it has a trigger word
                    if(title or content):
                        # block annoying posts
                        if (not conceptC and not conceptT and not concept2C and not concept2T and not concept3C and not concept3T):
                            # add the post to avoid reposts
                            if (new_timestamp == 0):
                                new_timestamp = submission.created
                            posted.append(submission.id)
                            no_repost.append(submission.id)

                            # send embed to the channel with the correct post
                            await send_embed(channel, submission)
        if (new_timestamp > 0):
            timestamp = new_timestamp
    except Exception as e:
        # avoid praw crashes when Reddit is lagging
        print("Error handled.")
    try:
        # for each new submissions in the req_limit
        for submission in subreddit.new(limit=req_limit):
            # for each headcanon trigger_words
            for word in trigger_words_hdcn:
                # if it's not a repost
                if (submission.created > timestamp and submission.id not in posted and submission.id not in no_repost):
                    # regex bullshit :clown:
                    title = re.search("\\b" + word + "\\b", submission.title.lower())
                    content = re.search("\\b" + word + "\\b", submission.selftext.lower())
                    # if it has a trigger word
                    if(title or content):
                        # add the post to avoid reposts
                        if (new_timestamp == 0):
                            new_timestamp = submission.created
                        posted.append(submission.id)
                        no_repost.append(submission.id)

                        # send embed to the channel with the correct post
                        await send_embed(channelHC, submission)
        if (new_timestamp > 0):
            timestamp = new_timestamp
    except Exception as e:
        # avoid praw crashes when Reddit is lagging
        print("Error handled.")

async def send_embed(chan, submission):
    # generate random number for the random agent
    random = randint(0, 15)

    # create embed according to the post and according to the agent
    embed = discord.Embed(color=agent_colors[random])
    embed.set_author(name="New Reddit Post", url="https://www.reddit.com/r/VALORANT/", icon_url="https://styles.redditmedia.com/t5_2dkvmc/styles/communityIcon_bd2cowmj92b51.png?width=256&s=a72824d1eae9ce77b2de79cc01f50c4cb692377e")
    embed.set_thumbnail(url=agent_base + agents[random])
    embed.add_field(name="Title", value=submission.title, inline=False)
    embed.add_field(name="Author", value=submission.author, inline=False)
    embed.add_field(name="Link", value=submission.url, inline=False)
    embed.set_footer(text=datetime.utcfromtimestamp(submission.created).strftime("%m/%d/%Y %H:%M") + " UTC")

    # send the embed
    await chan.send(embed=embed)

#######################

client.run("INSERT-BOT-TOKEN")
