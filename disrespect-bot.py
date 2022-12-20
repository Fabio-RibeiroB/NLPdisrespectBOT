import discord
import datetime
from dotenv import load_dotenv
import os
import logging
import nltk
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

TOKEN = os.getenv("TOKEN") 
#intents = discord.Intents(message_content=True)
#client = discord.Client(intents=intents)


intents = discord.Intents().all()
client = discord.Client(intents=intents)
 
  
#first event :logging in
@client.event
async def on_ready():
    print("successful login as {0.user}".format(client))
    global channel
    channel = client.get_channel(744677878465036358) # Replace with the ID of your Discord channel
    if channel == None:
        logger.info("None")

async def get_recent_messages(channel):
    """Get last 15000 messages"""
    messages = []
    logger.info("Getting recent messages...") 
    logger.info("Number of messages before loop: {}".format(len(messages)))
    async for message in channel.history(limit=15000):
        #if message.created_at > datetime.datetime.utcnow() - datetime.timedelta(days=7):
        if message.author != discord.Member.bot:
            messages.append(message)
    logger.info("Number of messages after loop: {}".format(len(messages)))
    return messages

async def main():
    logger.info("Starting nlp...")
    if channel is not None:
        logger.info("Channel is not null, channel retrieved...")
    else:
        logger.info("No client!")
    messages = await get_recent_messages(channel)

    logger.info("Recent messages retrieved")

    from nltk.sentiment.vader import SentimentIntensityAnalyzer

    sid = SentimentIntensityAnalyzer()

    sentiment_scores = {}

    for message in messages:
        
        # Ignore messages by bots
        if message.author == discord.Member.bot:
            logger.info("bot")
            return
        else:
            scores = sid.polarity_scores(message.content)
            sentiment = scores['compound']
            user_id = message.author.id
            if user_id in sentiment_scores:
                sentiment_scores[user_id] -= sentiment
            else:
                sentiment_scores[user_id] = sentiment

    
    global test_channel
    test_channel = client.get_channel(856947170798993448) # Replace with the ID of your Discord channel

    logger.info("User with most negative sentiment score found")
    await test_channel.send(f'I read the last 15000 messages in #general and used Natural Language Proeccessing to determine the most negative users.')
    sorted_scores = sorted(sentiment_scores.items(), key=lambda x: x[1])
    score_string = "SUPER USER NEGATIVITY\n"

    for i in range(1, 6):
        user, score = sorted_scores[i-1]
        score_string += f'{i}. <@{user}> {score}\n'


    await test_channel.send(score_string)
    logger.info("Message sent!")

logger.info("Waiting for message...")

@client.event
async def on_message(message):
    logger.info("There was a message...")
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # Check if the message starts with "!super-d"
    if message.content.startswith("!super-d"):
        logger.info("!super-d was typed...")
        # Call the main() function here
        await main()


client.run(TOKEN)
