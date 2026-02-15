#!/bin/bash
echo "🚀 [NyetRadio] Memulai Sinkronisasi & Auto-Patch Final..."

# 1. Bersihkan sisa-sisa tunnel lama agar tidak bentrok
pkill -f cloudflared
rm -f tunnel.log

# 2. Jalankan Tunnel dengan Header Host agar server Bedul mau melepas audio
echo "🔗 Menyambungkan Tunnel ke Server Radio (37.157.242.103)..."
cloudflared tunnel --url http://37.157.242.103:14303 --http-host-header 37.157.242.103 > tunnel.log 2>&1 &
CLOUDFLARE_PID=$!

echo "⏳ Menunggu link HTTPS Cloudflare (15 detik)..."
sleep 15

# 3. Ambil link HTTPS terbaru dari log
NEW_URL=$(grep -o 'https://[-0-9a-z]*\.trycloudflare.com' tunnel.log | head -n 1)

if [ -z "$NEW_URL" ]; then
    echo "❌ Gagal dapet link! Pastikan cloudflared sudah terinstal di Termux."
    kill $CLOUDFLARE_PID
    exit 1
fi

echo "✅ Link Baru: $NEW_URL"

# 4. Ambil index.html terbaru dari web Bedul
echo "📥 Mengambil source terbaru dari nyetradio.gt.tc..."
curl -s http://nyetradio.gt.tc/index.html -o index.html

# 5. Patching Agresif (Targeting link turtle-roger atau link cloudflare lainnya)
echo "🛠️ Melakukan Patching Link Audio..."
# Perintah sed ini akan mencari pola link trycloudflare lama dan menggantinya dengan yang baru + /;
sed -i "s|https://[^\"']*\.trycloudflare\.com[^\"']*|$NEW_URL/;|g" index.html

# 6. AUTO PUSH ke GitHub
echo "⬆️ Sinkronisasi ke GitHub..."
git add .
git commit -m "Auto Fix: HTTPS Audio Tunnel ($NEW_URL)"
git pull origin main --rebase  # Mencegah error rejected
git push origin main

echo "----------------------------------------------------------"
echo "🔥 GGWP! Link audio di HTML sudah otomatis terupdate."
echo "🔗 Cek di GitHub Pages lu dalam 1-2 menit ke depan."
echo "🎤 Mic lu harusnya udah bisa aktif sekarang karena jalur HTTPS!"
echo "----------------------------------------------------------"

# Menjaga tunnel tetap menyala selama lu siaran
wait $CLOUDFLARE_PID
