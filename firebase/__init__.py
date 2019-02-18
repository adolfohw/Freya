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
		guildsinfo[guild] = {'prefix': prefix}
	else:
		guildsinfo[guild]['prefix'] = prefix