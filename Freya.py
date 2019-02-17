import discord

from secret import TOKEN

bot = discord.Client()

@bot.event
async def on_ready():
	print('Freya online!')

bot.run(TOKEN)