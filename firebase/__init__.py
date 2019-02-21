# https://googleapis.github.io/google-cloud-python/latest/firestore/

import firebase_admin
from firebase_admin import credentials, db, firestore

cred = credentials.Certificate('./firebase/credentials.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client(app)

guildsinfo = {}

def set_prefix(guild: int, prefix: str):
	guild = str(guild)
	db.collection('guilds').document(guild).set({'prefix': prefix}, merge=True)
	if guild not in guildsinfo:
		guildsinfo[guild] = {}
	guildsinfo[guild]['prefix'] = prefix

def add_reaction_role(guild: int, msg: int, emoji, role: int):
	guild = str(guild)
	msg = str(msg)
	emoji = str(emoji)
	role = str(role)
	guild_db = db.collection('guilds').document(guild)
	guild_db.collection('reaction_roles').document(msg).set({
		emoji: role
	}, merge=True)
	if guild not in guildsinfo:
		guildsinfo[guild] = {}
	if 'reaction_roles' not in guildsinfo[guild]:
		guildsinfo[guild]['reaction_roles'] = {}
	if msg not in guildsinfo[guild]['reaction_roles']:
		guildsinfo[guild]['reaction_roles'][msg] = {}
	guildsinfo[guild]['reaction_roles'][msg][emoji] = role

def stop_watching_message(guild: int, msg='', all_msgs=False):
	guild = str(guild)
	msg = str(msg)
	try:
		guild_db = db.collection('guilds').document(guild)
		if all_msgs:
			docs = guild_db.collection('reaction_roles').get()
			for doc in docs:
				del guildsinfo[guild]['reaction_roles'][doc.id]
				doc.reference.delete()
			return
		guild_db.collection('reaction_roles').document(msg).delete()
		del guildsinfo[guild]['reaction_roles'][msg]
	except:
		raise KeyError