# Sentimental Analysis Discord bot

The motivation of this discord bot is to find the most negative user in the server using NLP.
This bot reads messages to create a leaderboard of negative users and deletes the message after 100s.

To run, create a `.env` with TOKEN=YOUR-BOT-TOKEN.
The bot reads user's messages only, going back by a specified amount.
Trigger the NLP with $disrespect [ENTER NO.].
E.g. $disrespect 10, to read the last 10 messages.

The output is board of the most negative users in the text channel.
