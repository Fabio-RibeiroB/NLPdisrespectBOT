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
    """Get last 100 messages"""
    messages = []
    logger.info("Getting recent messages...") 
    logger.info("Number of messages before loop: {}".format(len(messages)))
    async for message in channel.history(limit=100, oldest_first=True):
        #if message.created_at > datetime.datetime.utcnow() - datetime.timedelta(days=7):
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
        scores = sid.polarity_scores(message.content)
        sentiment = scores['compound']
        user_id = message.author.id
        if user_id in sentiment_scores:
            sentiment_scores[user_id] += sentiment
        else:
            sentiment_scores[user_id] = sentiment

    # Find the user with the lowest sentiment score
    most_negative_user = client.fetch_user(user_id)
    most_negative_score = float("inf") 
    for user_id, score in sentiment_scores.items():
        if score < most_negative_score:
            most_negative_user = user_id
            most_negative_score = score
    
    logger.info("User with most negative sentiment score found")
    await channel.send(f'I read the last 100 messages and used Natural Language Proeccessing to determine that <@{most_negative_user}> is the most negative. I am currently in BETA release. Read my code at: https://github.com/Fabio-RibeiroB/NLPdisrespectBOT')
    logger.info("Message sent!")

logger.info("Waiting for message...")

@client.event
async def on_message(message):
    logger.info("There was a message...")
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        return

    # Check if the message starts with "!disrespect"
    if message.content.startswith("!disrespect"):
        logger.info("!disrespect was typed...")
        # Call the main() function here
        await main()


client.run(TOKEN)


