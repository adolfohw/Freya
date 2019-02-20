import os

import discord
import discord.ext.commands as discordcmd

from firebase import db, guildsinfo
from secret import TOKEN

def get_prefix(bot, msg):
	guild = str(msg.guild.id)
	if guild in guildsinfo:
		return (guildsinfo[guild]['prefix'], 'f/')
	return ('!', 'f/')

bot = discordcmd.Bot(get_prefix)

async def deny_muted(channel):
	muted = discord.utils.get(channel.guild.roles, name='Muted')
	await channel.set_permissions(
		muted,
		add_reactions=False,
		read_messages=True,
		send_messages=False,
		send_tts_messages=False,
	)

@bot.event
async def on_guild_join(guild):
	if discord.utils.get(guild.roles, name='Muted') is None:
		await guild.create_role(
			name='Muted',
			color=discord.Color(0x36393f),
			mentionable=True,
			reason='Role used to stop members from posting in every channel'
		)
		channels = guild.text_channels
		for channel in channels:
			await deny_muted(channel)

@bot.event
async def on_guild_channel_create(channel):
	if discord.utils.get(channel.guild.roles, name='Muted'):
		await deny_muted(channel)

@bot.event
async def on_ready():
	guilds = db.collection('guilds').get()
	for guild in guilds:
		guildsinfo[guild.id] = guild.to_dict()
	print(f'Freya online!')

if __name__ == '__main__':
	for cog in os.listdir('./cogs'):
		if cog != '__pycache__':
			bot.load_extension(f'cogs.{cog.replace(".py", "")}')
	bot.run(TOKEN)