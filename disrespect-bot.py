import discord
import datetime

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as ')
    print(client.user.name)
    print(client.user.id)
    print('-----')

async def get_recent_messages(channel):
    messages = []
    
    async for message in channel.fetch_messages(limit=100):
        if message.created_at > datetime.datetime.utcnow() - datetime.timedelta(days=7):
            messages.append(message)

        return messages

from nltk.sentiment.vader import SentimentIntensityAnalyzer

sid = SentimentIntensityAnalyzer()
scores = sid.polarity_scores(message.content)
sentiment = scores['compound']

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
most_negative_user = None
most_negative_score = 0
for user_id, score in sentiment_scores.items():
    if score < most_negative_score:
        most_negative_user = user_id
        most_negative_score = score



channel = client.get_channel(654875602372919306) # Replace 1234567890 with the ID of your Discord channel
messages = await get_recent_messages(channel)

channel.send_message('The user with the most negative sentiment is: {}'.format(most_negative_user))


client.run('MTA1MDg3NTg5NTc1NTMyMTM5NA.GiI-hz.bzd738ylC32kYt6K2PIC3x7k2hlMa8_kwz67r4')


