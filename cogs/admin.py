from discord.ext import commands as cmd
from firebase import set_prefix

class Admin:
	def __init__(self, bot):
		self.bot = bot
	
	async def __local_check(self, ctx):
		return ctx.author.permissions_in(ctx.channel).administrator

	@cmd.command()
	async def prefix(self, ctx, arg):
		set_prefix(ctx.guild, arg)

def setup(bot):
	bot.add_cog(Admin(bot))