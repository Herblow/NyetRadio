import firebase_admin
from firebase_admin import credentials, db
import time
import requests

# 1. Konfigurasi Firebase
# Pastikan file key.json ada di folder yang sama
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://live-chat-nyet-default-rtdb.asia-southeast1.firebasedatabase.app'
})

def update_metadata():
    # URL JSON dari Icecast Termux
    url = "http://127.0.0.1:8000/status-json.xsl"
    print("--- NYETRADIO MONITORING STARTED (MediaCast Ready) ---")
    
    try:
        while True:
            try:
                # Ambil data dari Icecast
                response = requests.get(url, timeout=5)
                data = response.json()
                
                # Cek apakah ada source/penyiar yang sedang Connect
                if 'icestats' in data and 'source' in data['icestats']:
                    source = data['icestats']['source']
                    
                    # 1. Update Status jadi ON AIR
                    db.reference('status').update({'live': True})
                    
                    # 2. Ambil Judul & Artis (Handle jika MediaCast kirim data kosong)
                    # Jika source berupa list (multiple mount), ambil yang pertama
                    if isinstance(source, list):
                        source = source[0]
                        
                    title = source.get('title', 'Siaran Langsung')
                    artist = source.get('artist', 'NyetRadio')
                    
                    # Kirim Metadata ke Firebase
                    db.reference('nowPlaying').set({
                        'title': title,
                        'artist': artist
                    })
                    print(f"✅ ON AIR: {title} - {artist}")
                
                else:
                    # Jika tidak ada source yang terdeteksi
                    db.reference('status').update({'live': False})
                    db.reference('nowPlaying').set({'title': 'Offline', 'artist': 'Station'})
                    print("💤 OFF AIR: Menunggu koneksi dari MediaCast...")

            except requests.exceptions.ConnectionError:
                print("❌ Gagal konek ke Icecast! Pastiin Icecast udah jalan.")
                db.reference('status').update({'live': False})
            except Exception as e:
                print(f"⚠️ Error: {e}")
                db.reference('status').update({'live': False})
                
            # Cek setiap 5 detik agar tidak membebani Termux
            time.sleep(5) 
            
    except KeyboardInterrupt:
        # Jika script dihentikan (Ctrl+C), set status ke OFF
        db.reference('status').update({'live': False})
        print("\nStopping... Status diset ke OFF AIR.")

if __name__ == "__main__":
    update_metadata()
