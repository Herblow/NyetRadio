import requests
import time
import firebase_admin
from firebase_admin import credentials, db

# Koneksi ke Firebase pake file yang lu copy tadi
cred = credentials.Certificate('key.json')

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://live-chat-nyet-default-rtdb.asia-southeast1.firebasedatabase.app'
    })

ref = db.reference('nowPlaying')
ICECAST_URL = "http://127.0.0.1:8000/status-json.xsl"

print("📡 Script Auto-Metadata Nyala, Bos!")

while True:
    try:
        response = requests.get(ICECAST_URL, timeout=5)
        data = response.json()
        source = data['icestats']['source']
        if isinstance(source, list): source = source[0]

        info = {
            "title": source.get('title', 'Siaran Langsung'),
            "artist": source.get('artist', 'NyetRadio'),
            "status": "LIVE"
        }

        ref.set(info)
        print(f"🎵 Terkirim ke Firebase: {info['artist']} - {info['title']}")
        
    except Exception as e:
        print("Menunggu sinyal dari Broadcast Myself...")
        
    time.sleep(5)
