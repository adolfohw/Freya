from textwrap import shorten

from discord.ext import commands as cmd
from firebase import add_reaction_role, guildsinfo, stop_watching_message

class Roles:
	def __init__(self, bot):
		self.bot = bot

	async def get_reaction_parameters(self, rawreaction):
		msg_id = str(rawreaction.message_id)
		guild = self.bot.get_guild(rawreaction.guild_id)
		guild_id = str(rawreaction.guild_id)
		if guild_id in guildsinfo and msg_id in guildsinfo[guild_id]['reaction_roles']:
			emoji = rawreaction.emoji
			if emoji.is_custom_emoji():
				emoji = str(emoji.id)
			else:
				emoji = emoji.name
			try:
				role = guild.get_role(int(guildsinfo[guild_id]['reaction_roles'][msg_id][emoji]))
			except:
				raise KeyError
			member = guild.get_member(rawreaction.user_id)
			channel = guild.get_channel(rawreaction.channel_id)
			msg = await channel.get_message(rawreaction.message_id)
			
			return member, role, msg

	async def __local_check(self, ctx):
		return ctx.author.permissions_in(ctx.channel).administrator
		
	async def on_raw_reaction_add(self, rawreaction):
		try:
			member, role, msg = await self.get_reaction_parameters(rawreaction)
		except:
			return
		await member.add_roles(
			role,
			reason=f'Reacted to "{shorten(msg.content, 40, placeholder="...")}" in #{msg.channel.name} with {str(rawreaction.emoji.name)}'
		)
	
	async def on_raw_reaction_remove(self, rawreaction):
		try:
			member, role, msg = await self.get_reaction_parameters(rawreaction)
		except:
			return
		await member.remove_roles(
			role,
			reason=f'Removed {str(rawreaction.emoji.name)} reaction to "{shorten(msg.content, 40, placeholder="...")}" in #{msg.channel.name}'
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
	async def startwatching(self, ctx, msg_id: int, emoji, role: cmd.RoleConverter):
		"""Usage: ``!startwatching <MsgID> <Emoji> <Role>``

		``MsgID`` can be acquired by enabling Developer Mode in User Settings > Appearance, and right-clicking a message and selecting Copy ID;
		``Emoji`` can be either a unicode emoji or a server's custom emoji;
		``Role`` can be any reference to a role, e.g., @valkyrie, valkyrie"""
		
		if role.managed:
			await ctx.send(f'🙅‍ Sorry, but {role.name} is managed by an integration, so I cannot assign it to members')
			return
		for channel in ctx.guild.text_channels:
			try:
				msg = await channel.get_message(msg_id)
				break
			except:
				pass
		else:
			raise Exception('Message not found')

		# Custom emoji
		if len(emoji) > 1:
			emoji = await cmd.EmojiConverter().convert(ctx, emoji)
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

	@cmd.command()
	async def listmessages(self, ctx):
		placeholder = await ctx.send('🔎 Looking for messages...')
		try:
			msgs = guildsinfo[str(ctx.guild.id)]['reaction_roles']
			if not msgs:
				raise KeyError
		except:
			await placeholder.edit(content='✨ No messages are being watched', delete_after=3)
			return
		msg_list = '🕵️‍ Watching the following messages:\n\n'
		not_found = False
		unwatch_msgs = False
		for msg_id in msgs:
			for channel in ctx.guild.text_channels:
				try:
					msg = await channel.get_message(int(msg_id))
					break
				except:
					pass
			else:
				unwatch_msgs = True
				stop_watching_message(ctx.guild.id, msg)
				continue
			reaction_roles = []
			for raw_emoji, role in msgs[msg_id].items():
				if len(raw_emoji) > 1:
					emoji = self.bot.get_emoji(int(raw_emoji))
					if not emoji:
						try:
							emoji = await cmd.PartialEmojiConverter().convert(ctx, raw_emoji)
							emoji = str(emoji)
						except:
							emoji = '??'
				else:
					emoji = raw_emoji
				try:
					role = await cmd.RoleConverter().convert(ctx, role)
				except:
					role = '??'
				if '??' in (emoji, role):
					not_found = True
				reaction_roles.append(f'{str(emoji)} > {str(role)}')
			msg_list += f'**{msg_id}** - "{shorten(msg.content, 120, placeholder="...")}"\n{"; ".join(reaction_roles)}\n\n'
		if not_found:
			msg_list += '❗ If an emoji or role appears as ??, it means it is no longer visible to me, and I cannot properly manage that role.\n\n'
		if unwatch_msgs:
			msg_list += '🤷‍ Some messages appear to have been deleted, so I stopped watching them'
		await placeholder.edit(content=msg_list.strip())

	@cmd.command()
	async def stopwatching(self, ctx, msg_id: str):
		"""Usage: ``!stopwatching <MsgID or `all`>``
		
		``MsgID`` can be acquired by enabling Developer Mode in User Settings > Appearance, and right-clicking a message and selecting Copy ID;
		If ``all`` is passed instead, I will stop watching all messages"""

		guild_id = str(ctx.guild.id)
		if msg_id == 'all':
			try:
				stop_watching_message(guild_id, all_msgs=True)
				await ctx.send('👉 Stopped watching all messages')
			except KeyError:
				await ctx.send('🙇‍ Something happened and some messages are still being watched')
		else:
			try:
				if not msg_id in guildsinfo[guild_id]['reaction_roles']:
					raise KeyError
			except:
				await ctx.send('🙅‍ I am not watching that message')
				return
			stop_watching_message(guild_id, msg_id)
			await ctx.send(f'👉 Stopped watching message **{msg_id}**')

def setup(bot):
	bot.add_cog(Roles(bot))