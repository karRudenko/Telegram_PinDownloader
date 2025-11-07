import os
from telebot import TeleBot
from telebot.types import InlineQueryResultVideo, InlineQueryResultPhoto
import requests
from config import BOT_TOKEN
from functions import get_response, get_video_or_img_url, check_and_detect
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- Health Check Web Server (for Render & UptimeRobot) ---
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_health_server():
    port = int(os.getenv("PORT", 10000))  # Render assigns this automatically
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"🌐 Health server running on port {port}")
    server.serve_forever()

# Run health server in a background thread
threading.Thread(target=run_health_server, daemon=True).start()
# ------------------------------------------------------------------#

bot = TeleBot(BOT_TOKEN)
#-------------------------------------------------------------------#
@bot.inline_handler(lambda query: True)
def inline_pinterest(query):
    if not query.query:
        return
    
    urls_pins = check_and_detect(query.query)
    if urls_pins == []:
        bot.answer_inline_query(
            query.id,
            results=[],
            switch_pm_text="Send a Pinterest link here",
            switch_pm_parameter="start"
        )
        return
    
    results = []
    for idx, url_pin in enumerate(urls_pins):
        main_response = get_response(url_pin)
        res = get_video_or_img_url(main_response)
        print(res)

        if res in ["false_api", "false_response", "false_download_video_or_img_url"]:
            continue
        main_response = main_response.json()
        if main_response['type'] == 'video':
            try:
                results.append(
                    InlineQueryResultVideo(
                        id=f"video_{idx}",
                        video_url=res,
                        mime_type="video/mp4",
                        thumbnail_url=main_response['data']['thumbnail'],
                        title="Pinterest Video"
                    )
                )
            except Exception as e:
                print(e)
        elif main_response['type'] == 'image':
            try:
                results.append(
                    InlineQueryResultPhoto(
                        id=f"photo_{idx}",
                        photo_url=res,
                        thumbnail_url=res,
                        title="Pinterest Photo"
                    )
                )
            except Exception as e:
                print(e)
    if not results:
        bot.answer_inline_query(
            query.id,
            results=[],
            switch_pm_text="Could not get media - tap to send link",
            switch_pm_parameter="start"
        )
        return
    
    bot.answer_inline_query(query.id, results, cache_time=1)

#-------------------------------------------------------------------#

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(message, """
👋 Hi! Send me any Pinterest link and I will download the video or image for you.

Just paste the Pin URL here.
""")


@bot.message_handler(content_types=['text'])
def download_video(message):
    urls_pins = check_and_detect(message.text)
    if urls_pins == []:
        bot.reply_to(message, """
❓ It looks like your message does not contain a valid Pinterest link.  
Please send a correct Pin URL.
""")
        return None

    for url_pin in urls_pins:
        main_response = get_response(url_pin)
        res = get_video_or_img_url(main_response)

        if res == "false_api":
            bot.reply_to(message, "⚠️ Invalid Pinterest link. Please check the URL and try again.")
        elif res == "false_response":
            bot.reply_to(message, """
🚨 Sorry! There was a problem with the Pinterest server.  
Please try again later.  

If the problem continues, feel free to contact me: @Zipokpupok
""")
        elif res == "false_download_video_or_img_url":
            bot.reply_to(message, """
⚠️ Unable to retrieve media from Pinterest.  
Try another link or message me if you think this is a bug: @Zipokpupok
""")
        else:
            main_response = main_response.json()
            if main_response['type'] == 'video':
                response = requests.get(res, stream=True)
                try:
                    bot.send_video(
                    chat_id = message.chat.id,
                    video=response.raw,
                    duration=main_response['data']['duration'] // 1000,
                    width=main_response['data']['width'],
                    height=main_response['data']['height'],
                    thumb=main_response['data']['thumbnail']
                )
                except Exception as e:
                    print(e)
                    bot.reply_to(message, """
❌ I couldn't download this video.  
The file might be too large (Telegram limit: 50MB).  
Try another link
""")
            elif main_response['type'] == 'image':
                try:
                    bot.send_photo(
                    chat_id=message.chat.id,
                    photo=res
                )
                except Exception as e:
                    print(e)
                    bot.reply_to(message, """
❌ I couldn't download this image.  
The file might be too large (Telegram limit: 50MB).  
Try another image
""")

    return None


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, """
📸 Nice photo!  
But I only work with Pinterest links 😄
""")

@bot.message_handler(content_types=['video'])
def handle_video(message):
    bot.reply_to(message, "I had to send the video, not you...😢")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    bot.reply_to(message, """
📂 Got your file — but I only work with Pinterest links.
""")
#------------------------------------------------------------------#

try:
    bot.infinity_polling()
except KeyboardInterrupt:
    print("\n🛑 Bot stopped by user")
except Exception as e:
    print(f"❌ Bot error: {e}")
