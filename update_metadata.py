import firebase_admin
from firebase_admin import credentials, db
import time
import requests

# 1. Konfigurasi Firebase
# Pastikan file key.json ada di folder yang sama dengan script ini
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://live-chat-nyet-default-rtdb.asia-southeast1.firebasedatabase.app'
})

def update_metadata():
    # URL JSON dari Icecast Termux
    url = "http://127.0.0.1:8000/status-json.xsl"
    print("--- MONITORING SERVER DIMULAI ---")

    try:
        while True:
            try:
                # Ambil data dari Icecast
                response = requests.get(url, timeout=5)
                data = response.json()

                # Cek apakah ada penyiar yang sedang Connect
                if 'icestats' in data and 'source' in data['icestats']:
                    source = data['icestats']['source']
                    if isinstance(source, list):
                        source = source[0]

                    # AMBIL DATA ASLI (Kalo kosong, tampilkan Unknown)
                    title = source.get('title', 'Unknown Title')
                    artist = source.get('artist', 'Unknown Artist')

                    # 1. Update Status jadi ON AIR
                    db.reference('status').update({'live': True})

                    # 2. Kirim Metadata ke Firebase
                    db.reference('nowPlaying').set({
                        'title': title,
                        'artist': artist
                    })
                    print(f"✅ ON AIR: {artist} - {title}")

                else:
                    # Jika tidak ada siaran (OFF AIR)
                    db.reference('status').update({'live': False})
                    db.reference('nowPlaying').set({
                        'title': 'Offline',
                        'artist': 'Station'
                    })
                    print("💤 OFF AIR: Menunggu siaran...")

            except requests.exceptions.ConnectionError:
                print("❌ Gagal konek ke Icecast! Pastiin Icecast lu jalan.")
                db.reference('status').update({'live': False})
            except Exception as e:
                print(f"⚠️ Error: {e}")

            # Cek setiap 5 detik
            time.sleep(5) 

    except KeyboardInterrupt:
        db.reference('status').update({'live': False})
        print("\nScript dihentikan.")

if __name__ == "__main__":
    update_metadata()
