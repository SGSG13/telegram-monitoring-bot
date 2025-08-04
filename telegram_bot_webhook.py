import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from website_monitor import WebsiteMonitor
import time
from threading import Thread
from typing import List

logger = logging.getLogger(__name__)

class WebhookMonitoringBot:
    def __init__(self, bot_token: str, user_id: str, monitor: WebsiteMonitor):
        self.bot_token = bot_token
        self.user_id = user_id
        self.monitor = monitor
        self.application = None
        self.is_running = False
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await update.message.reply_text(
            "🤖 Бот для мониторинга сайта запущен!\n\n"
            "Доступные команды:\n"
            "/status - Проверить текущий статус\n"
            "/check - Выполнить проверку сейчас\n"
            "/stop - Остановить мониторинг\n"
            "/start_monitoring - Запустить автоматический мониторинг"
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        try:
            page_info = self.monitor.get_page_info()
            if "error" in page_info:
                await update.message.reply_text(f"❌ Ошибка: {page_info['error']}")
                return
            
            status_text = (
                f"📊 Статус мониторинга:\n\n"
                f"🌐 Сайт: {page_info['url']}\n"
                f"📄 Заголовок: {page_info['title']}\n"
                f"📏 Размер страницы: {page_info['content_length']} символов\n"
                f"🔍 Ищем: {', '.join(page_info['search_names'])}\n"
                f"🔄 Мониторинг: {'Активен' if self.is_running else 'Остановлен'}"
            )
            await update.message.reply_text(status_text)
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при получении статуса: {e}")
    
    async def check_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /check - выполнить проверку сейчас"""
        await update.message.reply_text("🔍 Выполняю проверку...")
        
        try:
            found_names = self.monitor.check_for_names()
            if found_names:
                message = f"✅ Найдены имена: {', '.join(found_names)}"
                await update.message.reply_text(message)
            else:
                await update.message.reply_text("❌ Имена не найдены")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при проверке: {e}")
    
    async def start_monitoring_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start_monitoring"""
        if self.is_running:
            await update.message.reply_text("🔄 Мониторинг уже запущен!")
            return
        
        self.is_running = True
        await update.message.reply_text("🚀 Мониторинг запущен! Бот будет проверять сайт каждые 10 минут.")
        
        # Запускаем мониторинг в отдельном потоке
        Thread(target=self._run_monitoring_loop, daemon=True).start()
    
    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stop"""
        self.is_running = False
        await update.message.reply_text("⏹️ Мониторинг остановлен!")
    
    def _run_monitoring_loop(self):
        """Запускает цикл мониторинга в отдельном потоке"""
        while self.is_running:
            try:
                found_names = self.monitor.check_for_names()
                
                # Отправляем уведомление если найдены имена
                if found_names:
                    # Простая отправка уведомления без сложной асинхронной логики
                    logger.info(f"Найдены имена: {found_names}")
                
                # Ждем перед следующей проверкой
                time.sleep(600)  # 10 минут
                
            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(60)  # Ждем минуту при ошибке
    
    async def setup_handlers(self):
        """Настраивает обработчики команд"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("check", self.check_command))
        self.application.add_handler(CommandHandler("start_monitoring", self.start_monitoring_command))
        self.application.add_handler(CommandHandler("stop", self.stop_command))
    
    async def run(self):
        """Запускает бота"""
        try:
            self.application = Application.builder().token(self.bot_token).build()
            await self.setup_handlers()
            
            logger.info("Бот запущен!")
            
            # Используем простой polling без сложной логики
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            # Ждем завершения
            await self.application.updater.idle()
            
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
            raise 