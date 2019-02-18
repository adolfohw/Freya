from discord.ext import commands as cmd
from firebase import set_prefix

class Admin:
	def __init__(self, bot):
		self.bot = bot
	
	async def __local_check(self, ctx):
		return ctx.author.permissions_in(ctx.channel).administrator
	
	async def __error(self, ctx, err):
		ctx.send('Insufficient permission')
		raise err

	@cmd.command()
	async def prefix(self, ctx, arg):
		"""Changes the command prefix. Every command can always be invoked with f!"""
		
		set_prefix(ctx.guild.id, arg)
		await ctx.send(f'\\👉 Prefix changed from ``{ctx.prefix}`` to ``{arg}``\nYou can always invoke commands using ``f!`` if you forget your custom prefix')

def setup(bot):
	bot.add_cog(Admin(bot))