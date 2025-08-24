<<<<<<< HEAD
FROM python:3.9-slim

# Установка ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .

# Запуск приложения
=======
FROM python:3.9-slim

# Установка ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .

# Запуск приложения
>>>>>>> c5dd15e62cd9c1a5d1e3d146a2fb320956f4f8a2
CMD ["python", "app.py"]