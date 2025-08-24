from flask import Flask, request, render_template_string
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time

app = Flask(__name__)

# Spotify API ключи (замените на ваши, если нужно)
SPOTIFY_CLIENT_ID = 'cc7178053fc144e4882daa5d29caa285'
SPOTIFY_CLIENT_SECRET = 'ed6bf45b1e3f41ab84edf3aa2a697fa8'

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    if request.method == 'POST':
        service = request.form.get('service')
        url = request.form.get('url')
        if service == 'youtube':
            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'extract_flat': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    time.sleep(5)  # Задержка для избежания бота-защиты
                    formats = info['formats']
                    audio_url = next((f['url'] for f in formats if f['acodec'] != 'none' and f['vcodec'] == 'none'), None)
                    video_url = next((f['url'] for f in formats if f['vcodec'] != 'none'), None)
                    result = "<h3>Ссылки для скачивания YouTube:</h3>"
                    if video_url:
                        result += f"<a href='{video_url}' style='color: #4774fc;'>Скачать MP4 (видео)</a><br>"
                    if audio_url:
                        result += f"<a href='{audio_url}' style='color: #4774fc;'>Скачать MP3 (аудио)</a><br>"
            except Exception as e:
                if "DRM" in str(e):
                    result = "<p class='error'>Контент защищён DRM и не может быть скачан.</p>"
                elif "Sign in to confirm" in str(e):
                    result = "<p class='error'>Требуется подтверждение от YouTube. Попробуйте позже или используйте другой трек.</p>"
                else:
                    result = f"<p class='error'>Ошибка YouTube: {str(e)}</p>"
        elif service == 'spotify':
            try:
                sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))
                track_id = url.split('/')[-1].split('?')[0]  # Извлечение Track ID
                track = sp.track(track_id)
                name = track['name']
                artist = track['artists'][0]['name']
                query = f"{artist} {name} official audio"
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'extract_flat': True,
                    'default_search': 'ytsearch10',
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=False)
                    time.sleep(5)  # Задержка для избежания бота-защиты
                    if 'entries' in info and info['entries']:
                        yt_url = info['entries'][0]['url']
                        info_yt = ydl.extract_info(yt_url, download=False)
                        formats = info_yt['formats']
                        audio_url = next((f['url'] for f in formats if f['acodec'] != 'none' and f['vcodec'] == 'none'), None)
                        video_url = next((f['url'] for f in formats if f['vcodec'] != 'none'), None)
                        result = f"Spotify трек: {name} от {artist}<br><h3>Найдено на YouTube и ссылки для скачивания:</h3>"
                        if video_url:
                            result += f"<a href='{video_url}' style='color: #4774fc;'>Скачать MP4 (видео)</a><br>"
                        if audio_url:
                            result += f"<a href='{audio_url}' style='color: #4774fc;'>Скачать MP3 (аудио)</a><br>"
                    else:
                        result = "<p class='error'>Трек не найден на YouTube.</p>"
            except Exception as e:
                if "DRM" in str(e):
                    result = "<p class='error'>Контент защищён DRM и не может быть скачан.</p>"
                elif "Sign in to confirm" in str(e):
                    result = "<p class='error'>Требуется подтверждение от YouTube. Попробуйте позже или используйте другой трек.</p>"
                else:
                    result = f"<p class='error'>Ошибка Spotify: {str(e)}</p>"
    return render_template_string("""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Media Downloader</title>
    <style>
        body { display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #0a020f; margin: 0; font-family: Arial, sans-serif; }
        .container { text-align: center; padding: 20px; border-radius: 10px; background-color: rgba(26, 26, 42, 0.8); }
        h1 { color: #4774fc; margin-bottom: 20px; }
        .input-group { margin: 15px 0; }
        input[type="text"] { width: 400px; padding: 10px; border: 2px solid #1a1a2a; border-radius: 5px; background-color: #0a020f; color: #4774fc; font-size: 16px; }
        input[type="text"]:focus { outline: none; border-color: #4774fc; }
        button { padding: 10px 20px; margin-top: 10px; background-color: #1a1a2a; border: none; border-radius: 5px; color: #4774fc; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #2a2a4a; }
        .result { margin-top: 20px; color: #4774fc; }
        .error { color: #7e0221; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Media Downloader</h1>
        <div class="input-group">
            <form method="POST">
                <input type="text" name="url" placeholder="Введите ссылку Spotify[](https://...)" required>
                <br>
                <button type="submit" name="service" value="spotify">Обработать Spotify</button>
            </form>
        </div>
        <div class="input-group">
            <form method="POST">
                <input type="text" name="url" placeholder="Введите ссылку YouTube[](https://...)" required>
                <br>
                <button type="submit" name="service" value="youtube">Скачать с YouTube</button>
            </form>
        </div>
        <div class="result">
            {{ result | safe }}
        </div>
    </div>
</body>
</html>
""", result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)