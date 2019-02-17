# https://googleapis.github.io/google-cloud-python/latest/firestore/

import firebase_admin
from firebase_admin import credentials, db, firestore

cred = credentials.Certificate('./firebase/credentials.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client(app)

def set_prefix(guild: int, prefix: str):
	db.collection(u'guilds').document(guild).set({u'prefix': prefix.encode()}, merge=True)