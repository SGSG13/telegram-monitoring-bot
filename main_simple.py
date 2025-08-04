import asyncio
import logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID, TARGET_URL, SEARCH_NAMES, CHECK_INTERVAL_MINUTES, LOG_LEVEL
from website_monitor import WebsiteMonitor
from telegram_bot import MonitoringBot

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

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
    logger.info("Запуск бота для мониторинга сайта...")
    
    # Проверяем конфигурацию
    if not validate_config():
        logger.error("Некорректная конфигурация. Проверьте переменные окружения")
        return
    
    try:
        # Создаем монитор сайта
        monitor = WebsiteMonitor(TARGET_URL, SEARCH_NAMES)
        
        # Создаем и запускаем бота
        bot = MonitoringBot(TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID, monitor)
        
        logger.info("✅ Бот запущен и готов к работе!")
        
        # Запускаем бота правильно
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        import traceback
        logger.error(f"Полная ошибка: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(main()) 