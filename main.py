import asyncio
import logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID, TARGET_URL, SEARCH_NAMES, CHECK_INTERVAL_MINUTES, LOG_LEVEL
from website_monitor import WebsiteMonitor
from telegram_bot import MonitoringBot
from aiohttp import web
import os

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Глобальная переменная для хранения бота
bot_instance = None

async def healthcheck_handler(request):
    """Обработчик для healthcheck"""
    return web.Response(text="OK", status=200, content_type='text/plain')

async def start_web_server():
    """Запускает веб-сервер для healthcheck"""
    try:
        app = web.Application()
        app.router.add_get('/', healthcheck_handler)
        app.router.add_get('/health', healthcheck_handler)
        
        # Добавляем обработчик ошибок
        async def error_handler(request):
            return web.Response(text="Internal Server Error", status=500)
        
        app.router.add_get('/error', error_handler)
        
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Запуск веб-сервера на порту {port}")
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        
        logger.info(f"✅ Веб-сервер успешно запущен на порту {port}")
        return runner
    except Exception as e:
        logger.error(f"❌ Ошибка запуска веб-сервера: {e}")
        raise

def validate_config():
    """Проверяет корректность конфигурации"""
    errors = []
    
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN не установлен")
    
    if not TELEGRAM_USER_ID:
        errors.append("TELEGRAM_USER_ID не установлен")
    
    if not TARGET_URL:
        errors.append("TARGET_URL не установлен")
    
    if not SEARCH_NAMES or not any(SEARCH_NAMES):
        errors.append("SEARCH_NAMES не установлены")
    
    if errors:
        logger.error("Ошибки конфигурации:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    
    return True

async def main():
    """Главная функция"""
    global bot_instance
    
    logger.info("Запуск бота для мониторинга сайта...")
    
    # Проверяем конфигурацию
    if not validate_config():
        logger.error("Некорректная конфигурация. Проверьте переменные окружения")
        return
    
    # Запускаем веб-сервер для healthcheck
    web_runner = await start_web_server()
    
    try:
        # Создаем монитор сайта
        monitor = WebsiteMonitor(TARGET_URL, SEARCH_NAMES)
        
        # Создаем и запускаем бота
        bot_instance = MonitoringBot(TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID, monitor)
        
        # Запускаем бота в фоне
        bot_task = asyncio.create_task(bot_instance.run())
        
        # Ждем завершения бота
        await bot_task
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        # Останавливаем веб-сервер
        await web_runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 