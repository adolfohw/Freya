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

async def deny_muted(channel):
	muted = discord.utils.get(channel.guild.roles, name='Muted')
	await channel.set_permissions(
		muted,
		reason='Stop Muted members from posting and reacting',
		add_reactions=False,
		send_messages=False,
		send_tts_messages=False,
	)

class Mod:
	def __init__(self, bot):
		self.bot = bot
	
	async def __local_check(self, ctx):
		return ctx.author.permissions_in(ctx.channel).ban_members

	async def __error(self, ctx, err):
		msg = await ctx.send('🤚 You do not have permission to do that')
		asyncio.sleep(3)
		await msg.delete()
		raise err

	async def on_guild_channel_create(self, channel):
		if discord.utils.get(channel.guild.roles, name='Muted'):
			await deny_muted(channel)	

	async def on_guild_join(self, guild):
		if discord.utils.get(guild.roles, name='Muted') is None:
			await guild.create_role(
				name='Muted',
				color=discord.Color(0x36393f),
				reason='Role used to stop members from posting in every channel'
			)
			channels = guild.text_channels
			for channel in channels:
				await deny_muted(channel)

	@cmd.command()
	async def mute(self, ctx, *args):
		"""Usage: ``!mute <Member> (Time) (Reason)``

		``Member`` can be a mention or any reference to a member, e.g., @John, John#1234, or John;
		``Time`` (optional) can be any number followed by d, h, m, s or nothing (defaults to s);
		``Reason`` (optional) will be displayed in the audit log and relayed to the muted member"""

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
				reason='Asked to mute without having a Muted role'
			)
		elif muted in member.roles:
			return
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
		await ctx.send(f'🙊 Muted {member.display_name} for{time} for {reason}')
		if wait:
			await asyncio.sleep(wait)
			if muted in member.roles:
				await member.remove_roles(muted, reason='Punishment time elapsed')
				if not member.bot:
					await member.send(f'🎉 You are free to speak in {ctx.guild.name} again!')
	
	@cmd.command()
	async def unmute(self, ctx, *args):
		"""Usage: ``!unmute <Member> (Reason)``
		
		``Member`` can be a mention or any reference to a member, e.g., @John, John#1234, or John;
		``Reason`` (optional) will be displayed in the audit log and relayed to the muted member"""

		try:
			member = await cmd.MemberConverter().convert(ctx, args[0])
		except:
			await ctx.send(ctx.command.help)
			return
		muted = discord.utils.get(ctx.guild.roles, name='Muted')
		if muted and muted in member.roles:
			reason = 'no reason'
			if len(args) > 1:
				reason = ' '.join(args[1:])
			await member.remove_roles(muted, reason=reason.capitalize())
			await ctx.send(f'👉 {member.display_name} has been unmuted for {reason}')
			if not member.bot:
				await member.send(f'🎉 {ctx.author.display_name} unmuted you in {ctx.guild.name} for {reason}')
	
	@cmd.command()
	async def kick(self, ctx, *args):
		"""Usage: ``!kick <Member> (Reason)``

		``Member`` can be a mention or any reference to a member, e.g., @John, John#1234, or John;
		``Reason`` (optional) will be displayed in the audit log and relayed to the kicked member"""
		
		try:
			member = await cmd.MemberConverter().convert(ctx, args[0])
		except:
			await ctx.send(ctx.command.help)
			return
		reason = 'no reason'
		if len(args) > 1:
			reason = ' '.join(args[1:])
		if not member.bot:
			await member.send(f'👢 {ctx.author.display_name} kicked you in {ctx.guild.name} for {reason}')
		await member.kick(reason=reason.capitalize())
		await ctx.send(f'👢 {member.display_name} has been kicked for {reason}')
	
	@cmd.command()
	async def ban(self, ctx, *args):
		"""Usage: ``!ban <Member> (Reason)``

		``Member`` can be a mention or any reference to a member, e.g., @John, John#1234, or John;
		``Reason`` (optional) will be displayed in the audit log and relayed to the banned member"""
		
		try:
			member = await cmd.MemberConverter().convert(ctx, args[0])
		except:
			await ctx.send(ctx.command.help)
			return
		reason = 'no reason'
		if len(args) > 1:
			reason = ' '.join(args[1:])
		if not member.bot:
			await member.send(f'🔨 {ctx.author.display_name} banned you in {ctx.guild.name} for {reason}')
		await member.ban(reason=reason.capitalize())
		await ctx.send(f'🔨 {member.display_name} has been banned for {reason}')

	@cmd.command()
	async def unban(self, ctx, *args):
		"""Usage: ``!unban <User> (Reason)``

		``User`` can be a mention or any reference to a user, e.g., @John, John#1234, or John;
		``Reason`` (optional) will be displayed in the audit log and relayed to the banned member (if possible)"""
		
		try:
			for _, banned in await ctx.guild.bans():
				if args[0] in (
					banned.mention,
					banned.id, 
					banned.name, 
					f'{banned.name}#{banned.discriminator}',
					banned.display_name
				):
					user = banned
					break
		except:
			await ctx.send(ctx.command.help)
			return
		reason = 'no reason'
		if len(args) > 1:
			reason = ' '.join(args[1:])
		try:
			await user.send(f'🎉 {ctx.author.display_name} unbanned you in {ctx.guild.name} for {reason}')
		except:
			pass
		finally:
			await ctx.guild.unban(user, reason=reason.capitalize())
			await ctx.send(f'👉 {user.display_name} has been unbanned for {reason}')

def setup(bot):
	bot.add_cog(Mod(bot))