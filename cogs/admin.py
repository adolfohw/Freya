from discord.ext import commands as cmd
from firebase import guildsinfo, set_prefix

class Admin(cmd.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	async def __local_check(self, ctx):
		return ctx.author.permissions_in(ctx.channel).administrator

	@cmd.command()
	async def prefix(self, ctx, arg):
		"""Usage: ``!prefix <Prefix>``

		Every command can always be invoked with ``f/``"""
		
		cur_prefix = guildsinfo[str(ctx.guild.id)]['prefix'] if str(ctx.guild.id) in guildsinfo else '!'
		set_prefix(ctx.guild.id, arg)
		await ctx.send(f'👉 Prefix changed from ``{cur_prefix}`` to ``{arg}``\nYou can always invoke commands using ``f/`` if you forget your custom prefix')
	
	@cmd.command()
	async def logchannel(self, ctx, channel: cmd.TextChannelConverter):
		pass

def setup(bot):
	bot.add_cog(Admin(bot))