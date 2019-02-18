import asyncio
import re

import discord
from discord.ext import commands as cmd

time_mod = {
	'd': 86400,
	'h': 3600,
	'm': 60,
	's': 1
}

class Mod:
	def __init__(self, bot):
		self.bot = bot
	
	async def __local_check(self, ctx):
		return ctx.author.permissions_in(ctx.channel).ban_members

	async def __error(self, ctx, err):
		await ctx.send('Insufficient permission')
		raise err
	
	@cmd.command()
	async def mute(self, ctx, *args):
		"""Usage: ``!mute <Member> (Time) (Reason)``

		``Member`` can be a mention or any reference to a member; e.g., @John, John#1234, or John;
		``Time`` (optional) can be any number followed by d, h, m, s or nothing (defaults to s);
		``Reason`` (optional) will be display in the audit log and relayed to the muted member"""

		if args and args[0]:
			try:
				member = await cmd.MemberConverter().convert(ctx, args[0])
			except:
				await ctx.send(ctx.command.help)
				return
		muted = discord.utils.get(ctx.guild.roles, name='Muted')
		if muted is None:
			muted = await ctx.guild.create_role(
				name='Muted',
				color=discord.Color(0x36393f),
				mentionable=True,
				reason='Asked to mute without having a Muted role'
			)
		wait = None
		time = 'ever'
		reason = 'no reason'
		if len(args) > 1:
			time = re.search(r'\d+?(?=(d|h|m|s|)$)', args[1])
			if time:
				unit = time.groups()[0] if time.groups()[0] else 's'
				wait = float(time.group())*time_mod[unit]
				time = f' {int(wait)}{unit}'
				if len(args) > 2:
					reason = ' '.join(args[2:]) 
			else:
				reason = ' '.join(args[1:])
		await member.add_roles(muted, reason=reason.capitalize())
		await member.send(f'🙊 {ctx.author.display_name} muted you in {ctx.guild.name} for{time} for {reason}')
		await ctx.send(f'🙊 Muted {member.mention} for{time} for {reason}')
		if wait:
			await asyncio.sleep(wait)
			if muted in member.roles:
				await member.remove_roles(muted, reason='Punishment time elapsed')
				await member.send(f'🎉 You are free to speak in {ctx.guild.name} again!')
	
	@cmd.command()
	async def unmute(self, ctx, member):
		"""Usage: ``!unmute <Member>``
		
		``Member`` can be a mention or any reference to a member; e.g., @John, John#1234, or John"""
		try:
			member = await cmd.MemberConverter().convert(ctx, member)
		except:
			await ctx.send(ctx.command.help)
			return
		muted = discord.utils.get(ctx.guild.roles, name='Muted')
		if muted and muted in member.roles:
			await member.remove_roles(muted)
			await member.send(f'🎉 {ctx.author.display_name} unmuted you in {ctx.guild.name}')
			await ctx.send(f'👉 {member.mention} has been unmuted')
	
	@cmd.command()
	async def kick(self, ctx, *args):
		pass
	
	@cmd.command()
	async def ban(self, ctx, *args):
		pass
	
	@cmd.command()
	async def unban(self, ctx, *args):
		pass

def setup(bot):
	bot.add_cog(Mod(bot))