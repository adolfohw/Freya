import os

import discord
import discord.ext.commands as cmd

from firebase import db, guildsinfo
from secret import TOKEN

# All IDs are integers in the form of strings 
# guildsinfo = {
# 	'guild_id': {
# 		'prefix': str,
# 		'reaction_roles': {
# 			'msg_id': {
# 				'unicode_emoji_or_emoji_id': 'role_id'
# 			}
# 		}
# 	}
# }

def get_prefix(bot, msg):
	guild = str(msg.guild.id)
	if guild in guildsinfo:
		try:
			return (guildsinfo[guild]['prefix'], 'f/')
		except:
			pass
	return ('!', 'f/')

bot = cmd.Bot(get_prefix)

@bot.event
async def on_command_error(ctx, err):
	if isinstance(err, cmd.CheckFailure):
		await ctx.message.delete()
		await ctx.send('🤚 You do not have permission to do that', delete_after=3)
	else:
		await ctx.send(ctx.command.help)

@bot.event
async def on_ready():
	guilds = db.collection('guilds').stream()
	for guild in guilds:
		try:
			guildsinfo[guild.id] = guild.to_dict()
			reaction_roles = guild.reference.collection('reaction_roles').stream()
			guildsinfo[guild.id]['reaction_roles'] = {msg.id: msg.to_dict() for msg in reaction_roles}
		except:
			pass
	n_guilds = len(bot.guilds)
	print(f'Freya online!\nServing {n_guilds} guild{"s" if n_guilds != 1 else ""}.')

if __name__ == '__main__':
	for cog in os.listdir('./cogs'):
		if cog != '__pycache__':
			bot.load_extension(f'cogs.{cog.replace(".py", "")}')
	bot.run(TOKEN)