from textwrap import shorten

import discord
from discord.ext import commands as cmd
from firebase import add_reaction_role, guildsinfo

class Roles:
	def __init__(self, bot):
		self.bot = bot
	
	async def __local_check(self, ctx):
		return ctx.author.permissions_in(ctx.channel).administrator
		
	async def on_raw_reaction_add(self, rawreaction):
		msg_id = str(rawreaction.message_id)
		guild = self.bot.get_guild(rawreaction.guild_id)
		guild_id = str(rawreaction.guild_id)
		if guild_id in guildsinfo and msg_id in guildsinfo[guild_id]['reaction_roles']:
			emoji = rawreaction.emoji
			if emoji.is_custom_emoji():
				emoji = str(emoji.id)
			else:
				emoji = emoji.name
			role = guild.get_role(int(guildsinfo[guild_id]['reaction_roles'][msg_id][emoji]))
			member = guild.get_member(rawreaction.user_id)
			channel = guild.get_channel(rawreaction.channel_id)
			msg = await channel.get_message(rawreaction.message_id)
			await member.add_roles(
				role,
				reason=f'Reacted to "{shorten(msg.content, 40, placeholder="...")}" in #{channel.name} with {str(rawreaction.emoji.name)}'
			)
	
	async def on_raw_reaction_remove(self, rawreaction):
		msg_id = str(rawreaction.message_id)
		guild = self.bot.get_guild(rawreaction.guild_id)
		guild_id = str(rawreaction.guild_id)
		if guild_id in guildsinfo and msg_id in guildsinfo[guild_id]['reaction_roles']:
			emoji = rawreaction.emoji
			if emoji.is_custom_emoji():
				emoji = str(emoji.id)
			else:
				emoji = emoji.name
			role = guild.get_role(int(guildsinfo[guild_id]['reaction_roles'][msg_id][emoji]))
			member = guild.get_member(rawreaction.user_id)
			channel = guild.get_channel(rawreaction.channel_id)
			msg = await channel.get_message(rawreaction.message_id)
			await member.remove_roles(
				role,
				reason=f'Removed {str(rawreaction.emoji.name)} reaction to "{shorten(msg.content, 40, placeholder="...")}" in #{channel.name}'
			)

	async def on_ready(self):
		for guild_id in guildsinfo:
			guild = self.bot.get_guild(int(guild_id))
			for msg_id, reactions in guildsinfo[guild_id]['reaction_roles'].items():
				for channel in guild.text_channels:
					try:
						msg = await channel.get_message(int(msg_id))
						break
					except:
						pass
				else:
					return
				remaining_emojis = list(reactions)
				for reaction in msg.reactions:
					emoji = reaction.emoji
					if not isinstance(emoji, str):
						emoji = str(emoji.id)
					if emoji in reactions:
						remaining_emojis.remove(emoji)
						role = guild.get_role(int(reactions[emoji]))
						reaction_users = await reaction.users().flatten()
						for member in reaction_users:
							try:
								if role not in member.roles:
									await member.add_roles(
										role,
										reason=f'Reacted to "{shorten(msg.content, 40, placeholder="...")}" in #{msg.channel.name} with {reaction.emoji.name}'
									)
							except:
								pass
						emoji = reaction.emoji
						if not isinstance(emoji, str):
							emoji = emoji.name
						for member in role.members:
							if member not in reaction_users:
								await member.remove_roles(
									role,
									reason=f'Not subscribed to {emoji} in "{shorten(msg.content, 40, placeholder="...")}" in #{msg.channel.name}'
								)
				for emoji in remaining_emojis:
					role = guild.get_role(int(reactions[emoji]))
					for member in role.members:
						await member.remove_roles(
							role,
							reason=f'Not subscribed to {emoji} in "{shorten(msg.content, 40, placeholder="...")}" in #{msg.channel.name}'
						)

	@cmd.command()
	async def reactionrole(self, ctx, msg_id: int, emoji, role: cmd.RoleConverter):
		"""Usage: ``!reactionrole <MsgID> <Emoji> <Role>``

		``MsgID`` can be acquired by enabling Developer Mode in User Settings > Appearance, and right-clicking a message and selecting Copy ID;
		``Emoji`` can be either a unicode emoji or a server's custom emoji;
		``Role`` can be any reference to a role, e.g., @valkyrie, valkyrie"""
		
		if role.managed:
			await ctx.send(f'🙅‍ Sorry, but {role.name} is managed by an integration and cannot be assigned')
			return
		for channel in ctx.guild.text_channels:
			try:
				msg = await channel.get_message(msg_id)
				break
			except:
				pass
		else:
			ctx.send(ctx.command.help)
			return

		# Custom emoji
		if len(emoji) > 1:
			try:
				emoji = await cmd.EmojiConverter().convert(ctx, emoji)
			except:
				await ctx.send(ctx.command.help)
				return
		for reaction in msg.reactions:
			if reaction.emoji == emoji:
				async for member in reaction.users():
					try:
						await member.add_roles(
							role,
							reason=f'Reacted to "{shorten(msg.content, 40, placeholder="...")}" in #{msg.channel.name} with {str(emoji)}'
						)
					except:
						pass
		add_reaction_role(ctx.guild.id, msg.id, emoji if isinstance(emoji, str) else emoji.id , role.id)
		await ctx.send(f'🎭 Reacting to "{shorten(msg.content, 40, placeholder="...")}" with {str(emoji)} will now grant the {role.name} role to members')

def setup(bot):
	bot.add_cog(Roles(bot))