#!/bin/bash
echo "🚀 [NyetRadio] Memulai Sinkronisasi Total..."

# 1. Bersihkan log lama
rm -f tunnel.log

# 2. Jalankan Cloudflare Tunnel di background
cloudflared tunnel --url http://127.0.0.1:8000 > tunnel.log 2>&1 &
CLOUDFLARE_PID=$!

echo "⏳ Menunggu link Cloudflare (15 detik)..."
sleep 15

# 3. Ambil link HTTPS terbaru
NEW_URL=$(grep -o 'https://[-0-9a-z]*\.trycloudflare.com' tunnel.log | head -n 1)

if [ -z "$NEW_URL" ]; then
    echo "❌ Gagal dapet link Cloudflare! Cek koneksi internet lu."
    kill $CLOUDFLARE_PID
    exit 1
fi

echo "✅ Link Baru Ditemukan: $NEW_URL"

# 4. Update link di index.html secara otomatis
sed -i "s|https://.*\.trycloudflare\.com|$NEW_URL|g" index.html

# 5. AUTO PUSH (Fitur Baru & Link Baru)
echo "⬆️ Mengirim update fitur & link ke GitHub..."
git add .
git commit -m "Auto Update: Fitur Baru & Link Tunnel ($NEW_URL)"
git push origin main

echo "🔥 GGWP! Web Lu udah versi terbaru dan link udah ONLINE."
echo "💡 Sekarang silakan jalankan 'python update_metadata.py' di tab baru."

# Menjaga tunnel tetap jalan
wait $CLOUDFLARE_PID
