import time
import pyrebase
import requests
import re
import json

# ==========================================
# 1. KONFIGURASI FIREBASE
# ==========================================
config = {
    "apiKey": "AIzaSyDV5K8-zseYUbtzK7QJAkyN-UnILiSFOkg",
    "authDomain": "live-chat-nyet.firebaseapp.com",
    "databaseURL": "https://live-chat-nyet-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "live-chat-nyet",
    "storageBucket": "live-chat-nyet.firebasestorage.app"
}

# Inisialisasi koneksi ke Firebase
try:
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    print("🔥 Firebase Connected!")
except Exception as e:
    print(f"❌ Gagal konek Firebase: {e}")
    exit()

# ==========================================
# 2. KONFIGURASI YOUTUBE (COOKIE)
# ==========================================
# PASTIKAN COPY SEMUA COOKIE DARI BROWSER DI SINI
COOKIE = "MASUKIN_COOKIE_FULL_LU_DI_SINI"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": COOKIE,
    "Content-Type": "application/json",
    "Origin": "https://music.youtube.com",
    "Referer": "https://music.youtube.com/history"
}

# ==========================================
# 3. FUNGSI AMBIL DATA (CORE)
# ==========================================
def get_now_playing():
    url = "https://music.youtube.com/youtubei/v1/browse?prettyPrint=false"
    payload = {
        "context": {
            "client": {
                "clientName": "WEB_REMIX",
                "clientVersion": "1.20240101.01.00"
            }
        },
        "browseId": "FEmusic_history"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        raw_text = response.text
        
        # Cek apakah cookie masih hidup
        if "LOGIN_REQUIRED" in raw_text or "Sign in" in raw_text:
            return "ERROR_AUTH"

        # Cari videoId terbaru
        vid_match = re.search(r'"videoId":"([^"]+)"', raw_text)
        # Cari Judul lagu
        title_match = re.search(r'"title":\{"runs":\[\{"text":"([^"]+)"', raw_text)
        # Cari Nama Artis
        artist_match = re.search(r'"text":"([^"]+)","navigationEndpoint":\{"browseEndpoint":\{"browseId":"UC', raw_text)
        
        if vid_match and title_match:
            return {
                "id": vid_match.group(1),
                "title": title_match.group(1),
                "artist": artist_match.group(1) if artist_match else "Sugoisans"
            }
        return None

    except Exception as e:
        print(f"⚠️ Koneksi Error: {e}")
        return None

# ==========================================
# 4. LOOPING SYNC
# ==========================================
print("🦍 NYET-SYNC ULTIMATE: STANDBY...")
last_song_id = ""

while True:
    data = get_now_playing()
    
    if data == "ERROR_AUTH":
        print("❌ COOKIE EXPIRED! Ambil cookie baru dari browser sekarang.")
        time.sleep(60) # Tunggu semenit sebelum lapor lagi
        continue

    if data:
        # Jika lagu berbeda dengan yang sebelumnya
        if data['id'] != last_song_id:
            current_time = time.strftime("%H:%M:%S")
            print(f"[{current_time}] 🎵 SYNC: {data['artist']} - {data['title']}")
            
            try:
                # Update ke Firebase
                db.child("nowPlaying").set({
                    "artist": data['artist'],
                    "title": data['title'],
                    "updatedAt": current_time
                })
                # Set status radio live
                db.child("status").update({"live": True})
                
                last_song_id = data['id']
            except Exception as fb_err:
                print(f"⚠️ Gagal push ke Firebase: {fb_err}")
    else:
        print("⚠️ Menunggu lagu diputar di YouTube Music...")

    # Cek setiap 10 detik agar tidak membebani server/baterai
    time.sleep(10)
