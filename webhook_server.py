#!/data/data/com.termux/files/usr/bin/python
# -*- coding: utf-8 -*-

"""
NyetRadio Metadata Webhook Server
Auto-update metadata dari YouTube Music ke Firebase
"""

from flask import Flask, request, jsonify
import requests
import json
import re
from datetime import datetime

app = Flask(__name__)

# ===== KONFIGURASI =====
FIREBASE_URL = "https://live-chat-nyet-default-rtdb.asia-southeast1.firebasedatabase.app/nowPlaying.json"

# ===== FUNGSI PARSE NOTIFIKASI =====
def parse_notification(title, text):
    """
    Parse notifikasi YouTube Music
    Format bisa beda-beda tergantung versi:
    - "Judul Lagu" (title) dan "Nama Artis" (text)
    - "Nama Artis - Judul Lagu" (di salah satu field)
    """
    
    artist = "Unknown Artist"
    song_title = "Unknown Track"
    
    # Method 1: Cek apakah ada format "Artist - Title"
    if " - " in title:
        parts = title.split(" - ", 1)
        artist = parts[0].strip()
        song_title = parts[1].strip()
    elif " - " in text:
        parts = text.split(" - ", 1)
        artist = parts[0].strip()
        song_title = parts[1].strip()
    else:
        # Method 2: Assume title = song, text = artist
        song_title = title.strip() if title else "Unknown Track"
        artist = text.strip() if text else "Unknown Artist"
    
    # Clean up common patterns
    artist = re.sub(r'\s+', ' ', artist)  # Remove extra spaces
    song_title = re.sub(r'\s+', ' ', song_title)
    
    # Remove common suffixes
    artist = re.sub(r'\s*-\s*Topic$', '', artist)
    song_title = re.sub(r'\s*\(.*?\)$', '', song_title)  # Remove (Official Video) etc
    
    return {
        "artist": artist,
        "title": song_title,
        "timestamp": datetime.now().isoformat(),
        "source": "auto"
    }

# ===== ENDPOINT WEBHOOK =====
@app.route('/update-metadata', methods=['POST'])
def update_metadata():
    """
    Terima POST dari MacroDroid dengan notifikasi data
    """
    try:
        data = request.get_json() or {}
        
        # Ambil data dari request
        notification_title = data.get('title', '')
        notification_text = data.get('text', '')
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Notifikasi diterima:")
        print(f"  Title: {notification_title}")
        print(f"  Text: {notification_text}")
        
        # Parse notification
        metadata = parse_notification(notification_title, notification_text)
        
        print(f"  Parsed → Artist: {metadata['artist']}, Title: {metadata['title']}")
        
        # Update Firebase
        response = requests.patch(
            FIREBASE_URL,
            json=metadata,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"  ✓ Firebase updated successfully!")
            return jsonify({
                "success": True,
                "metadata": metadata,
                "message": "Metadata updated"
            }), 200
        else:
            print(f"  ✗ Firebase error: {response.status_code}")
            return jsonify({
                "success": False,
                "error": f"Firebase error: {response.status_code}"
            }), 500
            
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ===== ENDPOINT TEST =====
@app.route('/test', methods=['GET'])
def test():
    """Endpoint buat test server jalan atau nggak"""
    return jsonify({
        "status": "running",
        "server": "NyetRadio Metadata Webhook",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/manual-update', methods=['POST'])
def manual_update():
    """
    Update manual metadata (buat testing atau backup)
    POST with: {"artist": "...", "title": "..."}
    """
    try:
        data = request.get_json()
        artist = data.get('artist', 'Unknown Artist')
        title = data.get('title', 'Unknown Track')
        
        metadata = {
            "artist": artist,
            "title": title,
            "timestamp": datetime.now().isoformat(),
            "source": "manual"
        }
        
        response = requests.patch(FIREBASE_URL, json=metadata, timeout=10)
        
        if response.status_code == 200:
            return jsonify({"success": True, "metadata": metadata}), 200
        else:
            return jsonify({"success": False, "error": "Firebase error"}), 500
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ===== HEALTH CHECK =====
@app.route('/', methods=['GET'])
def home():
    return """
    <html>
    <head><title>NyetRadio Webhook</title></head>
    <body style="font-family: Arial; padding: 20px; background: #0f172a; color: white;">
        <h1>🎵 NyetRadio Metadata Webhook</h1>
        <p><strong>Status:</strong> <span style="color: #00ff00;">Running</span></p>
        <h3>Endpoints:</h3>
        <ul>
            <li><code>/update-metadata</code> - POST endpoint untuk MacroDroid</li>
            <li><code>/manual-update</code> - POST manual update</li>
            <li><code>/test</code> - Test server</li>
        </ul>
        <p style="color: #888;">Server time: {}</p>
    </body>
    </html>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# ===== MAIN =====
if __name__ == '__main__':
    print("=" * 50)
    print("🎵 NyetRadio Metadata Webhook Server")
    print("=" * 50)
    print("\n[INFO] Server starting on http://0.0.0.0:5000")
    print("[INFO] MacroDroid endpoint: http://localhost:5000/update-metadata")
    print("[INFO] Press Ctrl+C to stop\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
