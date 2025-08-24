from flask import Flask, request, render_template_string, send_from_directory, after_this_request
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import urllib.parse

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
                    'extract_flat': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    video_id = info['id']
                    result = "<h3>Ссылки для скачивания YouTube:</h3>"
                    result += f"<a href='/download/youtube/video/{video_id}' style='color: #4774fc;'>Скачать MP4 (видео)</a><br>"
                    result += f"<a href='/download/youtube/audio/{video_id}' style='color: #4774fc;'>Скачать MP3 (аудио)</a><br>"
            except Exception as e:
                if "DRM" in str(e):
                    result = "<p class='error'>Контент защищён DRM и не может быть скачан.</p>"
                elif "Sign in to confirm" in str(e):
                    result = "<p class='error'>Требуется подтверждение от YouTube. Попробуйте позже или используйте другой трек. Для обхода возрастных ограничений добавьте файл cookies.txt в корень проекта (см. инструкции в README).</p>"
                else:
                    result = f"<p class='error'>Ошибка YouTube: {str(e)}</p>"
        elif service == 'spotify':
            try:
                sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))
                track_id = url.split('/')[-1].split('?')[0]  # Извлечение Track ID
                track = sp.track(track_id)
                name = track['name']
                artist = track['artists'][0]['name']
                spotify_name = urllib.parse.quote(f"{name} - {artist}")
                query = f"{artist} {name} official audio"
                ydl_opts = {
                    'extract_flat': True,
                    'default_search': 'ytsearch10',
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=False)
                    if 'entries' in info and info['entries']:
                        yt_id = info['entries'][0]['id']
                        result = f"Spotify трек: {name} от {artist}<br><h3>Найдено на YouTube и ссылки для скачивания:</h3>"
                        result += f"<a href='/download/youtube/video/{yt_id}?spotify_name={spotify_name}' style='color: #4774fc;'>Скачать MP4 (видео)</a><br>"
                        result += f"<a href='/download/youtube/audio/{yt_id}?spotify_name={spotify_name}' style='color: #4774fc;'>Скачать MP3 (аудио)</a><br>"
                    else:
                        result = "<p class='error'>Трек не найден на YouTube.</p>"
            except Exception as e:
                if "DRM" in str(e):
                    result = "<p class='error'>Контент защищён DRM и не может быть скачан.</p>"
                elif "Sign in to confirm" in str(e):
                    result = "<p class='error'>Требуется подтверждение от YouTube. Попробуйте позже или используйте другой трек. Для обхода возрастных ограничений добавьте файл cookies.txt в корень проекта (см. инструкции в README).</p>"
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

@app.route('/download/youtube/<filetype>/<video_id>')
def download_youtube(filetype, video_id):
    if filetype not in ['audio', 'video']:
        return "Invalid type", 400
    ext = 'mp3' if filetype == 'audio' else 'mp4'
    tmp_file = f'/tmp/{video_id}.{ext}'
    url = f'https://www.youtube.com/watch?v={video_id}'
    try:
        ydl_opts = {
            'noplaylist': True,
        }
        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'
        if filetype == 'audio':
            ydl_opts.update({
                'format': 'bestaudio',
                'outtmpl': tmp_file,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': tmp_file,
            })
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        # Get download name
        spotify_name = request.args.get('spotify_name')
        if spotify_name:
            download_name = urllib.parse.unquote(spotify_name) + f'.{ext}'
        else:
            info_opts = {'quiet': True}
            if 'cookiefile' in ydl_opts:
                info_opts['cookiefile'] = ydl_opts['cookiefile']
            with yt_dlp.YoutubeDL(info_opts) as ydl_info:
                info = ydl_info.extract_info(url, download=False)
                download_name = f"{info['title']}.{ext}"
        response = send_from_directory('/tmp', f'{video_id}.{ext}', as_attachment=True, download_name=download_name)
        @after_this_request
        def remove_file(resp):
            try:
                os.remove(tmp_file)
            except Exception as error:
                app.logger.error(f"Error removing file {tmp_file}: {error}")
            return resp
        return response
    except Exception as e:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        error_msg = str(e)
        if "DRM" in error_msg:
            return "<p class='error'>Контент защищён DRM и не может быть скачан.</p>", 500
        elif "Sign in to confirm" in error_msg:
            return "<p class='error'>Требуется подтверждение от YouTube. Для обхода добавьте cookies.txt (см. README).</p>", 500
        else:
            return f"<p class='error'>Ошибка: {error_msg}</p>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)