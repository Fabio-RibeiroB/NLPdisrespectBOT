import discord 
import logging
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
import pandas as pd
import pickle
from tabulate import tabulate
import numpy as np
nltk.downloader.download('vader_lexicon')

logger = logging.getLogger("my_bot")
logger.setLevel(logging.INFO)

# Create a handler to log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
# Create a formatter for the log messages
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Add the formatter to the console handler
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)
logger.info("Loading variables...")

load_dotenv()

intents = discord.Intents.all()
intents.members = True

client = commands.Bot(command_prefix = "$", intents = intents)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
  
async def get_recent_messages(ctx, limit):
    """Get the channel's messages going back by the amount specified by limit"""
    message_list = []
    async for message in ctx.channel.history(limit=limit, oldest_first=False, before=ctx.message):
        if not message.author.bot: 
            message_list.append(message)
    
    return message_list

@client.command()
async def disrespect(ctx, limit=None):

    logger.info("Starting nlp...")

    if limit is not None:
        limit = int(limit) # test this with letters        

    messages_list = await get_recent_messages(ctx, limit)
    
    message_count = len(messages_list)

    sid = SentimentIntensityAnalyzer()

    sentiment_scores = {}

    for message in messages_list:
        scores = sid.polarity_scores(message.content)
        sentiment = scores['compound']
        user_id = message.author.id
        if user_id in sentiment_scores:
            sentiment_scores[user_id] += sentiment
        else:
            sentiment_scores[user_id] = sentiment
    
    sentiment_board = pd.DataFrame(sentiment_scores, index=[0]).transpose()
    sentiment_board = sentiment_board.rename(columns={0: "score"})
    sentiment_board = sentiment_board.reset_index()
    sentiment_board = sentiment_board.rename(columns={"index": "user_id"})
    sentiment_board = sentiment_board.sort_values(by="score", ascending=True)

    sentiment_board["name"] = await asyncio.gather(*(get_name_from_id(id_) for id_ in sentiment_board["user_id"]))

    scores = sentiment_board["score"].values
    names = sentiment_board["name"].values
    index = np.arange(1, len(names)+1, 1) 

    await display_leaderboard(ctx, names, scores, message_count)
    print(tabulate(zip(index, names, scores), headers = ["", "Name", "Score"], tablefmt = "grid"))

async def get_name_from_id(user_id):
    user = await client.fetch_user(user_id)
    return user.name[:8]


async def display_leaderboard(ctx, names, scores, message_count):
    logger.info("Preparing leaderboard...")
    tot_users = len(names)
    num_pages = int(np.ceil(tot_users/10)) # 10 people per page
    index = np.arange(1, len(names)+1, 1)  # rank

    pages = []

    for i in range(num_pages):
        # Discord Embed
        page_i = discord.Embed(title = f"Negativity Board. Page {i+1}/{num_pages}", colour = discord.Colour.purple())

        # Partition into groups of 10
        names_i = names[i*10:(i+1)*10]
        index_i = index[i*10:(i+1)*10]
        scores_i = scores[i*10:(i+1)*10]
        scores_i = [f"{x:.3g}" for x in scores_i] # round scores 3sf
        
        # makes the page
        page_i.add_field(name = f"User messages found: {message_count}", value = "```"+tabulate(zip(index_i, names_i, scores_i), headers = ["", "Name", "Score"], tablefmt = "fancy_grid")+"```")

        pages.append(page_i)
        
    logger.info("Sending messages...")
    message = await ctx.send(embed = pages[0], delete_after=100)
    await message.add_reaction('⏮')
    await message.add_reaction('◀')
    await message.add_reaction('▶')
    await message.add_reaction('⏭')

    def check(reaction, user):
        """Check to ensure the message author has reacted"""
        return user == ctx.author

    i = 0
    reaction = None

    n = len(pages) # no. of pages

    # flip through the pages
    while True:
        if str(reaction) == '⏮': # go to page 1
            i = 0
            await message.edit(embed = pages[i])
        elif str(reaction) == '◀': # go back 1 page
            if i > 0:
                i -= 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '▶':
            if i < (n-1):
                i += 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '⏭':
            i = n-1
            await message.edit(embed = pages[i])
        
        try:
            # After 30s, bot will stop searching for reactions to leadboard
            reaction, user = await client.wait_for('reaction_add', timeout = 30.0, check = check)
            await message.remove_reaction(reaction, user)
        except:
            break # break on timeout

    await message.clear_reactions()

client.run(os.getenv("TOKEN"))
