import os
import urllib.parse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Настройки
TOKEN = '8371266802:AAFHfZi7LaPbP7G4O04G6gR5NdxtFL7lZbE'  # Ваш токен
SPOTIFY_CLIENT_ID = 'cc7178053fc144e4882daa5d29caa285'
SPOTIFY_CLIENT_SECRET = 'ed6bf45b1e3f41ab84edf3aa2a697fa8'

# Инициализация бота
app = Application.builder().token(TOKEN).build()

# Инициализация Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

def download_file(url, filetype):
    ext = 'mp4' if filetype == 'video' else 'mp3'
    tmp_file = f'/tmp/temp.{ext}'
    try:
        ydl_opts = {
            'noplaylist': True,
            'outtmpl': tmp_file,
        }
        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'
        if filetype == 'audio':
            ydl_opts['format'] = 'bestaudio'
        else:
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return tmp_file
    except Exception as e:
        error_msg = str(e)
        if "DRM" in error_msg:
            return "Контент защищён DRM и не может быть скачан."
        elif "Sign in to confirm" in error_msg:
            return "Требуется подтверждение от YouTube. Добавьте cookies.txt для обхода (см. инструкции)."
        else:
            return f"Ошибка: {error_msg}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет! Отправь мне ссылку на YouTube или Spotify в формате:\n'
        '/youtube URL\n'
        '/spotify URL\n'
        'Я постараюсь скачать MP4 или MP3. Для возрастных ограничений добавь cookies.txt.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    if message_text.startswith('/youtube'):
        url = message_text.replace('/youtube', '').strip()
        if not url:
            await update.message.reply_text('Пожалуйста, укажи URL после /youtube.')
            return
        await update.message.reply_text('Обрабатываю YouTube...')
        video_file = download_file(url, 'video')
        audio_file = download_file(url, 'audio')
        if isinstance(video_file, str) and 'Ошибка' in video_file:
            await update.message.reply_text(video_file)
        else:
            with open(video_file, 'rb') as f:
                await update.message.reply_video(f, caption='MP4 (видео)')
            os.remove(video_file)
            if audio_file and 'Ошибка' not in audio_file:
                with open(audio_file, 'rb') as f:
                    await update.message.reply_audio(f, caption='MP3 (аудио)')
                os.remove(audio_file)
    elif message_text.startswith('/spotify'):
        url = message_text.replace('/spotify', '').strip()
        if not url:
            await update.message.reply_text('Пожалуйста, укажи URL после /spotify.')
            return
        await update.message.reply_text('Обрабатываю Spotify...')
        try:
            track_id = url.split('/')[-1].split('?')[0]
            track = sp.track(track_id)
            name = track['name']
            artist = track['artists'][0]['name']
            query = f"{artist} {name} official audio"
            ydl_opts = {
                'default_search': 'ytsearch10',
                'extract_flat': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info and info['entries']:
                    yt_url = info['entries'][0]['url']
                    video_file = download_file(yt_url, 'video')
                    audio_file = download_file(yt_url, 'audio')
                    if isinstance(video_file, str) and 'Ошибка' in video_file:
                        await update.message.reply_text(video_file)
                    else:
                        with open(video_file, 'rb') as f:
                            await update.message.reply_video(f, caption=f'MP4 (видео): {name} - {artist}')
                        os.remove(video_file)
                        if audio_file and 'Ошибка' not in audio_file:
                            with open(audio_file, 'rb') as f:
                                await update.message.reply_audio(f, caption=f'MP3 (аудио): {name} - {artist}')
                            os.remove(audio_file)
                else:
                    await update.message.reply_text('Трек не найден на YouTube.')
        except Exception as e:
            await update.message.reply_text(f'Ошибка Spotify: {str(e)}')

# Обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Запуск бота
app.run_polling()