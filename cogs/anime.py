import math, random, textwrap, json
import urllib.request as url

import discord

from discord.ext import commands as cmd

# API: https://jikan.docs.apiary.io

RATING_COLOR = {
	'G': 0x80ffbb,
	'PG': 0xbbff80,
	'PG-13': 0xfff880,
	'R': 0xff8080,
	'R+': 0xcc80ff,
	'Rx': 0x000000
}

def get_suggestion():
	attempts = 0
	while attempts < 10:
		attempts += 1
		top_page = math.floor(random.uniform(1, 10))
		top_request = f'https://api.jikan.moe/v3/top/anime/{top_page}'
		try:
			with url.urlopen(top_request) as search:
				if search.getcode() != 200:
					continue
				data = json.load(search)
				suggestion = random.choice(data['top'])
				endpoint = 'http://api.jikan.moe/v3/anime/' + str(suggestion['mal_id'])
				with url.urlopen(endpoint) as anime:
					anime_data = json.load(anime)
					title = anime_data['title']
					title_url = anime_data['url']
					thumbnail = anime_data['image_url']
					# episodes = anime_data['episodes']
					kind = ' (' + anime_data['type'] + ')'
					rating = anime_data['rating'].partition(' ')[0]
					genres = [point['name'] for point in anime_data['genres']]
					description = anime_data['title_japanese'] \
						+ ' \\⭐ ' \
						+ str(anime_data['score']) \
						+ kind + '\n' \
						+ rating + ' - ' \
						+ ', '.join(genres)
					synopsis = anime_data['synopsis']
					anime_embed = discord.Embed(
						title=title,
						description=description,
						url=title_url,
						color=RATING_COLOR[rating]
					)
					anime_embed.set_thumbnail(url=thumbnail)
					anime_embed.add_field(
						name='Synopsis',
						value=textwrap.shorten(synopsis, width=500, placeholder='...')
					)
					return anime_embed
		except:
			continue

class Anime(cmd.Cog):
	buffer = None

	def __init__(self, bot):
		self.bot = bot
		self.buffer = get_suggestion()

	@cmd.command()
	async def anime(self, ctx):
		"""Usage: ``!anime <`new`>``

		Suggests a new anime for you!"""

		if self.buffer is None:
			await ctx.send("👉 I couldn't find an anime for you, try again later")
		else:
			await ctx.send(embed=self.buffer)
		self.buffer = get_suggestion()

def setup(bot):
	bot.add_cog(Anime(bot))

if __name__ == '__main__':
	get_suggestion()