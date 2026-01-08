"""
Telegram бот с командами для управления
"""
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import config
from datetime import datetime
import asyncio


class TelegramBotCommands:
    def __init__(self, monitor):
        """
        monitor - экземпляр PriceSpreadMonitor
        """
        self.monitor = monitor
        self.start_time = datetime.now()
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        welcome_message = """
🤖 <b>MEXC Price Spread Monitor</b>

Бот отслеживает разницу между последней ценой и справедливой ценой на всех фьючерсных парах MEXC.

<b>Доступные команды:</b>
/start - Показать это сообщение
/status - Статус бота
/stats - Статистика работы

<b>Настройки:</b>
📊 Отслеживаю: <code>{}</code> пар
⚠️ Порог алерта: <code>{}%</code>
🔔 Cooldown: <code>{} минут</code>

Бот работает в режиме реального времени!
""".format(
            len(self.monitor.symbols),
            config.MIN_SPREAD_PERCENT,
            config.ALERT_COOLDOWN // 60
        )
        
        await update.message.reply_text(welcome_message, parse_mode='HTML')
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /status"""
        uptime = datetime.now() - self.start_time
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        
        status_message = f"""
📊 <b>Статус бота</b>

🟢 Статус: <b>Активен</b>
⏱ Работает: <code>{hours}ч {minutes}м</code>
📈 Сканирований: <code>{self.monitor.scan_counter}</code>
🔔 Всего алертов: <code>{self.monitor.total_alerts}</code>
📊 Мониторинг: <code>{len(self.monitor.symbols)}</code> пар

⚡️ Режим: <b>Непрерывное сканирование</b>
"""
        
        await update.message.reply_text(status_message, parse_mode='HTML')
    
    async def cmd_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stats"""
        uptime = datetime.now() - self.start_time
        scans_per_minute = self.monitor.scan_counter / (uptime.total_seconds() / 60) if uptime.total_seconds() > 0 else 0
        
        stats_message = f"""
📊 <b>Детальная статистика</b>

<b>Общее:</b>
• Выполнено сканирований: <code>{self.monitor.scan_counter}</code>
• Отправлено алертов: <code>{self.monitor.total_alerts}</code>
• Скорость: <code>{scans_per_minute:.1f}</code> сканирований/мин

<b>Настройки:</b>
• Порог спреда: <code>{config.MIN_SPREAD_PERCENT}%</code>
• Cooldown: <code>{config.ALERT_COOLDOWN}с</code>
• Отслеживаемые пары: <code>{len(self.monitor.symbols)}</code>

<b>Активные алерты в cooldown:</b>
<code>{len(self.monitor.analyzer.alert_history)}</code> пар
"""
        
        await update.message.reply_text(stats_message, parse_mode='HTML')
    
    def setup_handlers(self, app: Application):
        """Настроить обработчики команд"""
        app.add_handler(CommandHandler("start", self.cmd_start))
        app.add_handler(CommandHandler("status", self.cmd_status))
        app.add_handler(CommandHandler("stats", self.cmd_stats))
