        
import os
import yt_dlp

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

TOKEN = "8860159120:AAEO9I_aRqbLNlHtiIVHeX2Cjo7xQHPJmus"

user_links = {}

# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
👋 Welcome to PS Download and Convert

📥 Download videos from:
• YouTube
• TikTok
• Facebook

🎵 Convert videos to MP3
🎥 Download videos in MP4

📎 Send your video link to start!
"""

    await update.message.reply_text(text)

# RECEIVE LINK
async def receive_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text

    user_links[update.effective_user.id] = url

    keyboard = [
        [
            InlineKeyboardButton("🎥 MP4", callback_data="mp4"),
            InlineKeyboardButton("🎵 MP3", callback_data="mp3")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Choose format:",
        reply_markup=reply_markup
    )


# BUTTON CLICK
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    format_type = query.data

    url = user_links.get(user_id)

    if not url:
        await query.message.reply_text("No link found.")
        return

    await query.message.reply_text("⏳ Downloading...")

    try:

        # MP4
        if format_type == "mp4":

            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': '%(title)s.%(ext)s',
                'quiet': True,
                'noplaylist': True,
                'cookiefile': 'cookies.txt',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_name = ydl.prepare_filename(info)

            await query.message.reply_video(
                video=open(file_name, 'rb')
            )

            os.remove(file_name)

        # MP3
        elif format_type == "mp3":

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': '%(title)s.%(ext)s',
                'quiet': True,
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_name = ydl.prepare_filename(info)

            mp3_file = file_name.rsplit(".", 1)[0] + ".mp3"

            await query.message.reply_audio(
                audio=open(mp3_file, 'rb')
            )

            os.remove(mp3_file)

    except Exception as e:
        await query.message.reply_text(f"❌ Error:\n{e}")

# MAIN
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, receive_link)
)

app.add_handler(CallbackQueryHandler(button_click))

print("✅ Bot Running...")
app.run_polling()





