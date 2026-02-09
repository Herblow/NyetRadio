import firebase_admin
from firebase_admin import credentials, db
import time
import subprocess
import json

# 1. Konfigurasi Firebase
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://live-chat-nyet-default-rtdb.asia-southeast1.firebasedatabase.app'
})

def get_pano_metadata():
    try:
        # Panggil Termux:API buat list notifikasi
        result = subprocess.check_output(["termux-notification-list"], stderr=subprocess.DEVNULL)
        notifications = json.loads(result)
        
        # Cari notifikasi dari Pano Scrobbler (com.arn.scrobble)
        for n in notifications:
            if n.get('packageName') == "com.arn.scrobble":
                title = n.get('title', '')
                artist = n.get('content', '') # Pano pake 'content' buat nama artis
                
                # Pastiin judul gak kosong (biar gak nangkep notifikasi silent)
                if title:
                    return artist, title
        return None, None
    except Exception as e:
        print(f"⚠️ Error Termux:API: {e}")
        return None, None

def update_metadata():
    print("--- MONITORING NYETRADIO (PANO + TERMUX:API) ---")
    last_song = ""

    try:
        while True:
            artist, title = get_pano_metadata()

            if title and artist:
                current_song = f"{artist} - {title}"
                
                if current_song != last_song:
                    # Update Firebase
                    db.reference('status').update({'live': True})
                    db.reference('nowPlaying').set({
                        'title': title,
                        'artist': artist
                    })
                    print(f"✅ ON AIR: {artist} - {title}")
                    last_song = current_song
            else:
                # Jika notifikasi ilang atau lagu berhenti
                if last_song != "OFFLINE":
                    db.reference('status').update({'live': False})
                    db.reference('nowPlaying').set({
                        'title': 'Offline',
                        'artist': 'Station'
                    })
                    print("💤 OFF AIR: Menunggu musik diputar...")
                    last_song = "OFFLINE"

            time.sleep(3) # Cek tiap 3 detik

    except KeyboardInterrupt:
        db.reference('status').update({'live': False})
        print("\nScript dihentikan.")

if __name__ == "__main__":
    update_metadata()
