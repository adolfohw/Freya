import re

import discord

from discord.ext import commands as cmd

# Essentialy the same as MemberConverter, but slightly smarter
class ExtendedMemberConverter(cmd.IDConverter):
	async def convert(self, ctx, argument):
		message = ctx.message
		bot = ctx.bot
		match = self._get_id_match(argument) or re.match(r'<@!?([0-9]+)>$', argument)
		guild = ctx.guild
		result = None
		if match is None:
			argument = argument.lower()
			result = discord.utils.find(lambda match: argument == match.name.lower() or argument == match.display_name.lower(), guild.members)
		else:
			user_id = int(match.group(1))
			if guild:
				result = ctx.guild.get_member(user_id)
			else:
				result = cmd.converter._get_from_guilds(bot, 'get_member', user_id)

		return result

class Justice(cmd.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	@cmd.command()
	async def punish(self, ctx, *args):
		"""No rest for the wicked"""

		member = await ExtendedMemberConverter().convert(ctx, args[0])
		await ctx.send(f':omine::Whip: {member.mention}')

def setup(bot):
	bot.add_cog(Justice(bot))