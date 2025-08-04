#!/usr/bin/env python3
"""
Простой тестовый сервер для проверки healthcheck
"""
import asyncio
from aiohttp import web
import os

async def healthcheck_handler(request):
    """Обработчик для healthcheck"""
    return web.Response(text="OK", status=200, content_type='text/plain')

async def main():
    """Запуск тестового сервера"""
    app = web.Application()
    app.router.add_get('/', healthcheck_handler)
    app.router.add_get('/health', healthcheck_handler)
    
    port = int(os.environ.get('PORT', 8080))
    print(f"Запуск тестового сервера на порту {port}")
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    print(f"✅ Сервер запущен на http://localhost:{port}")
    print("Нажмите Ctrl+C для остановки")
    
    try:
        # Держим сервер запущенным
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Остановка сервера...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 