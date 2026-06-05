#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import yt_dlp
import requests
import tempfile
import os
import subprocess

# Ссылки на списки прокси из репозитория Vadim287/free-proxy
# 📡 Расширенный список источников прокси (источник: GitHub, авто-обновление)
PROXY_LISTS = {
    # === Основные и самые быстрые источники ===
    'hookzof_s5': 'https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt',
    'skillter_s5': 'https://raw.githubusercontent.com/Skillter/ProxyGather/main/socks5.txt',
    'zloi-user_s5': 'https://raw.githubusercontent.com/zloi-user/hideip.me/master/socks5.txt',
    'speedx_s5': 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt',

    # === Крупные агрегаторы и репозитории ===
    'proxyscrape_s5': 'https://raw.githubusercontent.com/ProxyScrape/free-proxy-list/main/proxies/protocols/socks5/data.txt',
    'thordata_s5': 'https://raw.githubusercontent.com/Thordata/awesome-free-proxy-list/main/proxies/socks5.txt',
    'komutan_s5': 'https://raw.githubusercontent.com/komutan234/Proxy-List-Free/main/proxies/socks5.txt',
    'proxRipper_s5': 'https://raw.githubusercontent.com/Mohammedcha/ProxRipper/main/full_proxies/socks5.txt',
    'fyvri_s5': 'https://raw.githubusercontent.com/fyvri/fresh-proxy-list/archive/storage/classic/socks5.txt',
    'vann-dev_s5': 'https://raw.githubusercontent.com/Vann-Dev/proxy-list/main/proxies/socks5.txt',
    'proxygenerator_s5': 'https://raw.githubusercontent.com/proxygenerator1/ProxyGenerator/main/MostStable/socks5.txt',
    'ian-lusule_s5': 'https://raw.githubusercontent.com/Ian-Lusule/Proxies/main/proxies/socks5.txt',
    'vadim287_s5': 'https://raw.githubusercontent.com/Vadim287/free-proxy/main/proxies/socks5.txt',

    # === Альтернативные и резервные источники ===
    'iplocate_s5': 'https://raw.githubusercontent.com/iplocate/free-proxy-list/main/protocols/socks5.txt',
    'clearproxy_s5': 'https://raw.githubusercontent.com/ClearProxy/checked-proxy-list/main/socks5/raw/all.txt',
    'joy-deploy_s5': 'https://raw.githubusercontent.com/thenasty1337/free-proxy-list/main/data/latest/types/socks5/proxies.txt',
    'firmfox_s5': 'https://raw.githubusercontent.com/Firmfox/proxify/main/proxies/socks5.txt',
    'theriturajps_s5': 'https://raw.githubusercontent.com/theriturajps/proxy-list/main/proxies.txt',
}


def install_ir_and_deno():
    """
    Устанавливает/обновляет install-release через pip,
    затем через ir устанавливает Deno.
    """
    print("📦 Настройка окружения...")

    # Шаг 1: Установка/обновление install-release
    print("  • Устанавливаю/обновляю install-release...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-U", "install-release"],
            capture_output=True,
            check=False
        )
        print("    ✅ install-release готов")
    except Exception as e:
        print(f"    ⚠️ Ошибка при установке install-release: {e}")

    # Шаг 2: Установка Deno через ir
    print("  • Устанавливаю Deno через ir...")
    try:
        # Добавляем PATH, если ir не найден
        env = os.environ.copy()
        home = os.path.expanduser("~")
        bin_path = os.path.join(home, "bin")
        if bin_path not in env.get("PATH", ""):
            env["PATH"] = f"{bin_path}:{env.get('PATH', '')}"

        result = subprocess.run(
            ["ir", "get", "https://github.com/denoland/deno"],
            capture_output=True,
            text=True,
            env=env
        )

        if result.returncode == 0:
            print("    ✅ Deno успешно установлен!")
            return True
        else:
            print(f"    ⚠️ Ошибка установки Deno: {result.stderr}")
            return False
    except FileNotFoundError:
        print("    ❌ Команда 'ir' не найдена даже после установки")
        return False
    except Exception as e:
        print(f"    ❌ Непредвиденная ошибка: {e}")
        return False


def ensure_deno_installed():
    """
    Проверяет наличие Deno, пытается установить, если его нет.
    """
    # Проверяем, есть ли Deno
    try:
        subprocess.run(['deno', '--version'], capture_output=True, check=True)
        print("✅ Deno уже установлен.")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("⚠️ Deno не найден. Пытаюсь установить автоматически...")
        return install_ir_and_deno()


def get_cookie_file():
    """
    Создает временный файл cookies из браузера Chrome для авторизации.
    """
    print("🍪 Извлекаю cookies из вашего браузера для авторизации...")
    try:
        import browser_cookie3
        cj = browser_cookie3.chrome(domain_name='youtube.com')
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmpfile:
            cookie_file = tmpfile.name
            for cookie in cj:
                tmpfile.write(
                    f"{cookie.domain}\tTRUE\t{cookie.path}\t{bool(cookie.secure)}\t{cookie.expires}\t{cookie.name}\t{cookie.value}\n")
        print("✅ Cookies успешно извлечены!")
        return cookie_file
    except ImportError:
        print("⚠️ Библиотека browser-cookie3 не найдена.")
        install = input("Установить browser-cookie3? (y/n): ").lower()
        if install == 'y':
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "browser-cookie3"], check=True)
                print("✅ browser-cookie3 установлен. Повторите попытку.")
            except Exception as e:
                print(f"❌ Ошибка установки: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Не удалось извлечь cookies: {e}")
        print("   Убедитесь, что вы вошли в YouTube в браузере Chrome.")
        return None


def check_proxy(proxy, test_url='https://www.youtube.com'):
    """Проверяет, работает ли прокси."""
    proxy_url = f'socks5://{proxy}'
    try:
        with yt_dlp.YoutubeDL({'proxy': proxy_url, 'quiet': True, 'socket_timeout': 5}) as ydl:
            ydl.extract_info(test_url, download=False)
        print(f"    ✅ Прокси {proxy} работает!")
        return proxy_url
    except Exception:
        return None


def get_working_proxy():
    """Загружает списки прокси из репозитория и возвращает URL первого рабочего."""
    print("\n🌐 Автоматический поиск рабочего прокси...")
    all_proxies = []
    for proxy_type, url in PROXY_LISTS.items():
        print(f"  Загружаю {proxy_type} прокси...")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                proxies = [line.strip() for line in response.text.splitlines() if line.strip()]
                if proxies:
                    print(f"    Загружено {len(proxies)} прокси.")
                    all_proxies.extend(proxies)
        except Exception as e:
            print(f"    ❌ Ошибка загрузки: {e}")
    if not all_proxies:
        print("❌ Не удалось загрузить ни один список прокси.")
        return None
    print(f"🔍 Всего загружено прокси для проверки: {len(all_proxies)}")
    for proxy in all_proxies:
        working_proxy = check_proxy(proxy)
        if working_proxy:
            print(f"✅ Выбран рабочий прокси: {proxy}")
            return working_proxy
    print("❌ Не найден ни один рабочий прокси.")
    return None


def download_video(url):
    """
    Основная функция скачивания с авторизацией, прокси и автоматической
    установкой Deno при необходимости.
    """
    # Убеждаемся, что Deno установлен
    if not ensure_deno_installed():
        print("⚠️ Продолжаем без Deno (некоторые форматы могут быть недоступны)")

    # Получаем cookies для авторизации
    cookie_file = get_cookie_file()

    # Находим рабочий прокси
    working_proxy = get_working_proxy()
    if not working_proxy:
        print("❌ Не удалось найти рабочий прокси. Попробуйте позже.")
        return False

    # Настройки yt-dlp
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': False,
        'no_warnings': False,
        'proxy': working_proxy,
        'cookies': cookie_file if cookie_file else None,
    }

    print(f"\n🚀 Начинаю скачивание...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\n✅ Скачивание успешно завершено!")
        return True
    except Exception as e:
        print(f"\n❌ Ошибка при скачивании: {e}")
        return False
    finally:
        if cookie_file and os.path.exists(cookie_file):
            os.unlink(cookie_file)
            print("🧹 Временный файл cookies удалён.")


def main():
    print("=== Умный загрузчик видео (с авторизацией) ===\n")

    # Получаем URL из аргументов командной строки или от пользователя
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Введите URL видео: ").strip()
        if not url:
            print("❌ URL не может быть пустым.")
            return

    success = download_video(url)
    if not success:
        print("Не удалось скачать видео. Проверьте подключение и повторите попытку.")


if __name__ == "__main__":
    main()