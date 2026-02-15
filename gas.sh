#!/bin/bash
echo "🚀 [NyetRadio] Memulai Sinkronisasi & Auto-Patch Jagoan..."

# 1. Bersihkan sisa perang lama
rm -f tunnel.log
pkill -f cloudflared

# 2. Jalankan Tunnel dengan Header Host (Biar suara keluar)
echo "🔗 Menyambungkan Tunnel ke Server Bedul (37.157.242.103)..."
# Ditambah --http-host-header biar Cloudflare bisa narik stream audio dengan benar
cloudflared tunnel --url http://37.157.242.103:14303 --http-host-header 37.157.242.103 > tunnel.log 2>&1 &
CLOUDFLARE_PID=$!

echo "⏳ Menunggu link HTTPS Cloudflare (15 detik)..."
sleep 15

# 3. Ambil link HTTPS terbaru
NEW_URL=$(grep -o 'https://[-0-9a-z]*\.trycloudflare.com' tunnel.log | head -n 1)

if [ -z "$NEW_URL" ]; then
    echo "❌ Gagal dapet link! Cek koneksi internet atau 'pkg install cloudflared' ulang."
    kill $CLOUDFLARE_PID
    exit 1
fi

echo "✅ Link Baru: $NEW_URL"

# 4. Ambil index.html terbaru & Patching
echo "📥 Mengambil source terbaru dari nyetradio.gt.tc..."
curl -s http://nyetradio.gt.tc/index.html -o index.html

echo "🛠️ Melakukan Patching Link Audio..."
# Kita pastiin ganti link HTTP lama (termasuk titik komanya) jadi link HTTPS baru
# Kita tambahin /; di belakang NEW_URL karena server radio Bedul butuh itu buat muter
sed -i "s|http://37.157.242.103:14303/;|$NEW_URL/;|g" index.html

# 5. AUTO PUSH ke GitHub
echo "⬆️ Sinkronisasi ke GitHub..."
git add .
git commit -m "Auto Fix: Audio HTTPS Tunnel via Cloudflare ($NEW_URL)"
git pull origin main --rebase
git push origin main

echo "----------------------------------------------------------"
echo "🔥 GGWP! Web lu sekarang sudah HTTPS penuh."
echo "🔗 Cek di: https://USERNAME_LU.github.io/REPRO_LU/"
echo "🎤 Mic lu harusnya udah bisa aktif sekarang di Kiwi Browser!"
echo "----------------------------------------------------------"

# Jaga tunnel tetap hidup
wait $CLOUDFLARE_PID
