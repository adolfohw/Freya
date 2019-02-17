import os

import discord.ext.commands as discord

from firebase import db
from secret import TOKEN

bot = discord.Bot(get_prefix)
guildsinfo = {}

def get_prefix(bot, msg):
	if msg.guild in guildsinfo:
		return guildsinfo[msg.guild]['prefix']
	return '!'

@bot.event
async def on_ready():
	guilds = db.collection(u'guilds').get()
	for guild in guilds:
		guildsinfo[guild.id] = guild.to_dict()
	print(f'Freya online!')
	print(guildsinfo)

if __name__ == '__main__':
	for cog in os.listdir('./cogs'):
		if cog != '__pycache__':
			bot.load_extension(f'cogs.{cog.replace(".py", "")}')
	bot.run(TOKEN)