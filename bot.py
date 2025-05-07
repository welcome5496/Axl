import os
import requests
import yt_dlp
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Load environment variables from .env (locally) or Render config
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# YouTube search
def search_youtube(query):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    return response.json()

# Download audio from YouTube
def download_audio(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegAudioConvertor',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        return filename, info['title']

# Telegram bot commands
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🎵 Welcome! Use /search <song name> to find music from YouTube.")

def search(update: Update, context: CallbackContext):
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("❗ Please provide a song name. Example: `/search Faded`", parse_mode='Markdown')
        return

    update.message.reply_text("🔍 Searching YouTube...")
    results = search_youtube(query)
    if results['items']:
        video = results['items'][0]
        video_id = video['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        title = video['snippet']['title']
        update.message.reply_text(f"🎧 Found: *{title}*\n📥 Downloading MP3...", parse_mode='Markdown')

        try:
            file_path, title = download_audio(video_url)
            with open(file_path, 'rb') as audio_file:
                update.message.reply_audio(audio_file, title=title)
        except Exception as e:
            update.message.reply_text(f"❌ Error: {str(e)}")
    else:
        update.message.reply_text("😕 No results found.")

def handle_error(update: Update, context: CallbackContext):
    print(f"Error: {context.error}")
    update.message.reply_text("❗ An unexpected error occurred.")

# Run the bot
def main():
    os.makedirs("downloads", exist_ok=True)
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("search", search))
    dp.add_error_handler(handle_error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
