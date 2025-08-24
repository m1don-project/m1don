# \# m1don

# 

# Flask-приложение для скачивания MP3/MP4 с YouTube и Spotify (через поиск на YouTube).

# 

# \## Установка и запуск

# 1\. Установите зависимости: `pip install -r requirements.txt`.

# 2\. Запустите: `python app.py`.

# 

# \## Деплой на Render

# \- Создайте Web Service на Render (Python).

# \- В Build Command добавьте: `apt-get update -y \&\& apt-get install -y ffmpeg` (для конвертации в MP3).

# \- В Start Command: `python app.py`.

# \- Добавьте переменные окружения для Spotify (если нужно свои ключи): SPOTIFY\_CLIENT\_ID и SPOTIFY\_CLIENT\_SECRET.

# 

# \## Обход возрастных ограничений (sign-in required)

# \- В браузере установите расширение "Get cookies.txt LOCALLY" (Chrome/Firefox).

# \- Залогиньтесь в YouTube.

# \- Экспортируйте cookies для домена `youtube.com` в файл `cookies.txt`.

# \- Добавьте `cookies.txt` в корень проекта и закоммитьте в GitHub.

# \- yt-dlp автоматически использует его для обхода age-gate.

# 

# \## Ограничения

# \- \*\*DRM\*\*: Невозможно обойти (защищенный контент).

# \- \*\*Rate limiting / Блокировки\*\*: Если Render IP заблокируют, используйте VPN или другой хостинг. Для личного использования — редко.

# \- \*\*Spotify\*\*: Не скачивает напрямую (API не позволяет), ищет на YouTube. Используйте свои Spotify ключи, если публичные заблокированы.

# \- \*\*Длинные видео\*\*: Могут вызвать таймаут на Render (увеличьте в настройках, если нужно).

