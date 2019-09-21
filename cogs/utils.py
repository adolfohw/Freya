import asyncio
import datetime
import re

import discord
from discord.ext import commands as cmd

time_mod = {
	'd': 86400,
	'h': 3600,
	'm': 60,
	's': 1
}

class Utils(cmd.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	@cmd.command(aliases=['rm'])
	async def remindme(self, ctx, *args):
		"""Usage: ``!remindme <Time> <Action>``
		
		Alias: ``!rm``
		``Time`` can be any number followed by d, h, m, s or nothing (defaults to s);
		``Action`` should be in the imperative mood for the reminder to make sense!"""

		try:
			time = re.search(r'\d+?(?=(d|h|m|s|)$)', args[0])
			reminder = ' '.join(args[1:])
		except:
			await ctx.send(ctx.command.help)
			return
		unit = time.groups()[0] if time.groups()[0] else 's'
		wait = float(time.group())*time_mod[unit]
		time = f'{int(wait)}{unit}'
		embed = discord.Embed(
			description=ctx.message.content,
			color=0xff325a if ctx.author.color.value == 0 else ctx.author.color,
			timestamp=datetime.datetime.now()
		)
		embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
		await ctx.send(f'⏳ I will remind you to "{reminder}" in {time}')
		await asyncio.sleep(wait)
		await ctx.author.send(f'🙋‍ Hey, don\'t forget to {reminder}!', embed=embed)

def setup(bot):
	bot.add_cog(Utils(bot))