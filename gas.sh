#!/bin/bash
echo "🚀 [NyetRadio] Memulai Sinkronisasi & Auto-Patch..."

# 1. Bersihkan log lama
rm -f tunnel.log

# 2. Jalankan Tunnel nembak ke IP Radio Bedul
echo "🔗 Menyambungkan Tunnel ke Server Radio (37.157.242.103)..."
cloudflared tunnel --url http://37.157.242.103:14303 > tunnel.log 2>&1 &
CLOUDFLARE_PID=$!

echo "⏳ Menunggu link HTTPS Cloudflare (15 detik)..."
sleep 15

# 3. Ambil link HTTPS terbaru
NEW_URL=$(grep -o 'https://[-0-9a-z]*\.trycloudflare.com' tunnel.log | head -n 1)

if [ -z "$NEW_URL" ]; then
    echo "❌ Gagal dapet link! Cek koneksi internet lu."
    kill $CLOUDFLARE_PID
    exit 1
fi

echo "✅ Link Baru: $NEW_URL"

# 4. Ambil index.html terbaru dari web Bedul & Patching
echo "📥 Mengambil source terbaru dari nyetradio.gt.tc..."
curl -s http://nyetradio.gt.tc/index.html -o index.html

echo "🛠️ Melakukan Patching Link Audio..."
# Mengganti link HTTP Bedul dengan link Tunnel HTTPS lu agar suara keluar
sed -i "s|http://37.157.242.103:14303/|$NEW_URL/|g" index.html

# 5. AUTO PUSH (Fix Rejected Error)
echo "⬆️ Sinkronisasi ke GitHub..."
git add .
git commit -m "Auto Fix: HTTPS Audio Tunnel ($NEW_URL)"
git pull origin main --rebase  # Biar gak rejected pas push
git push origin main

echo "🔥 GGWP! Web lu sekarang sudah HTTPS penuh dan suara DIJAMIN NYALA."
wait $CLOUDFLARE_PID
