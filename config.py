"""
Конфигурация для MEXC Price Spread Monitor
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram настройки
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_TOPIC_ID = os.getenv('TELEGRAM_TOPIC_ID')  # ID темы (опционально)

# MEXC API настройки
MEXC_BASE_URL = "https://contract.mexc.com"
MEXC_FUTURES_URL = "https://futures.mexc.com"

# Параметры мониторинга
MIN_SPREAD_PERCENT = 10.0  # Минимальный процент разницы для уведомления
SCAN_INTERVAL = 1  # Интервал между сканированиями в секундах (быстро, но без спама API)
ALERT_COOLDOWN = 300  # Пауза между повторными алертами для одной пары (5 минут, или +5% спред)

# Параметры запросов
REQUEST_TIMEOUT = 10  # Таймаут для HTTP запросов
MAX_RETRIES = 3  # Максимальное количество попыток при ошибке
