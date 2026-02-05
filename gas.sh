#!/bin/bash

echo "🚀 Menjalankan NyetRadio Auto-Update..."

# 1. Jalankan Cloudflare di background dan simpan log-nya
cloudflared tunnel --url http://127.0.0.1:8000 > tunnel.log 2>&1 &
CLOUDFLARE_PID=$!

echo "⏳ Menunggu link Cloudflare muncul..."
sleep 10

# 2. Ambil link dari file log
NEW_URL=$(grep -o 'https://[-0-9a-z]*\.trycloudflare.com' tunnel.log | head -n 1)

if [ -z "$NEW_URL" ]; then
    echo "❌ Gagal dapet link! Coba jalanin lagi."
    kill $CLOUDFLARE_PID
    exit 1
fi

echo "✅ Link Baru: $NEW_URL"

# 3. Update index.html pake perintah sed (Ganti line yang ada .trycloudflare.com)
sed -i "s|https://.*\.trycloudflare\.com|$NEW_URL|g" index.html

echo "⬆️ Push update ke GitHub..."
git add index.html
git commit -m "Auto-update link: $NEW_URL"
git push origin main

echo "🔥 GGWP! Radio lu udah online di: $NEW_URL"
echo "Tekan Ctrl+C buat berentiin tunnel."

# Jaga biar script tetep jalan
wait $CLOUDFLARE_PID
