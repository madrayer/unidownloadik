#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
import yt_dlp

def check_ffmpeg():
    """Проверяет, установлен ли ffmpeg в системе"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def get_formats(url):
    """Возвращает список доступных форматов для выбора"""
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = []
        for f in info.get('formats', []):
            # Фильтруем только форматы с видео+аудио или отдельно, но понятные пользователю
            if f.get('vcodec') != 'none' or f.get('acodec') != 'none':
                format_note = f.get('format_note', '')
                resolution = f.get('resolution', '')
                ext = f.get('ext', '')
                vcodec = f.get('vcodec', 'none')
                acodec = f.get('acodec', 'none')
                if vcodec != 'none' and acodec != 'none':
                    type_str = f'видео+аудио ({ext})'
                elif vcodec != 'none':
                    type_str = f'видео ({ext})'
                else:
                    type_str = f'аудио ({ext})'
                formats.append({
                    'id': f['format_id'],
                    'desc': f'{resolution} {format_note} {type_str}'.strip(),
                    'has_video': vcodec != 'none',
                    'has_audio': acodec != 'none'
                })
        return formats, info.get('title', 'Без названия')

def download_video(url, format_id=None):
    """Скачивает видео с указанным format_id (если None – лучший формат)"""
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',   # имя файла = название видео
        'quiet': False,                    # показывать прогресс
        'no_warnings': False,
    }
    if format_id:
        ydl_opts['format'] = format_id
    else:
        # Лучший формат видео+аудио
        ydl_opts['format'] = 'bestvideo+bestaudio/best'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            print("\n✅ Скачивание завершено!")
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

def main():
    print("=== Универсальный загрузчик видео (yt-dlp) ===\n")

    # 1. Проверка ffmpeg (для объединения видео+аудио)
    if not check_ffmpeg():
        print("⚠️  FFmpeg не найден. Видео могут скачиваться без звука или в низком качестве.")
        print("   Установите FFmpeg (инструкции в README).\n")

    # 2. Получение URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Введите URL видео: ").strip()
        if not url:
            print("URL не может быть пустым.")
            return

    print("\n🔍 Получаю информацию о видео...")
    try:
        formats, title = get_formats(url)
    except Exception as e:
        print(f"Не удалось получить данные: {e}")
        return

    print(f"\nНазвание: {title}")
    print("\nДоступные форматы:")
    for i, fmt in enumerate(formats, start=1):
        print(f"{i}. {fmt['desc']} (id={fmt['id']})")
    print(f"{len(formats)+1}. Скачать лучший (видео+аудио) автоматически")
    print(f"{len(formats)+2}. Выйти")

    # 3. Выбор формата
    choice = input(f"\nВыберите номер (1-{len(formats)+1}): ").strip()
    if not choice.isdigit():
        print("Неверный ввод. Завершаем.")
        return

    choice_num = int(choice)
    if choice_num == len(formats)+2:
        return
    elif choice_num == len(formats)+1:
        format_id = None
    elif 1 <= choice_num <= len(formats):
        format_id = formats[choice_num-1]['id']
    else:
        print("Некорректный выбор.")
        return

    # 4. Скачивание
    print("\n⏳ Скачивание началось...")
    download_video(url, format_id)

if __name__ == "__main__":
    main()