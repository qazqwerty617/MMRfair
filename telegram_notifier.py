"""
Telegram уведомления о спреде цен
"""
import requests
from typing import Dict
import config


class TelegramNotifier:
    def __init__(self):
        if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
            raise ValueError("TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID должны быть установлены в .env")
        
        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
    
    def format_message(self, alert_data: Dict) -> str:
        """Форматировать сообщение о спреде (Visual Style)"""
        symbol = alert_data['symbol']
        last_price = alert_data['last_price']
        fair_price = alert_data['fair_price']
        spread_percent = alert_data['spread_percent']
        
        # Определяем сторону (Side)
        # Если Last > Fair (спред +), значит перекуплен -> SHORT
        # Если Last < Fair (спред -), значит недооценен -> LONG
        if spread_percent > 0:
            side = "short"
            emoji = "🔴"
        else:
            side = "long"
            emoji = "🟢"
            
        # Формируем сообщение как на скрине
        # HOLO 10.24%
        # Fair price: 0.09504
        # Last price: 0.08578
        # Side: 🟢 long
        
        message = f"""
<u>{symbol}</u> <b>{abs(spread_percent):.2f}%</b>

Fair price: <code>{fair_price:.6f}</code>
Last price: <code>{last_price:.6f}</code>

Side: {emoji} <b>{side}</b>
"""
        return message.strip()
    
    def send_alert_sync(self, alert_data: Dict):
        """Отправить уведомление в Telegram (синхронно)"""
        try:
            message = self.format_message(alert_data)
            
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            # Если задан ID темы, добавляем его
            if config.TELEGRAM_TOPIC_ID:
                try:
                    payload['message_thread_id'] = int(config.TELEGRAM_TOPIC_ID)
                except ValueError:
                    print(f"⚠️ Ошибка: TELEGRAM_TOPIC_ID '{config.TELEGRAM_TOPIC_ID}' не является числом")
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=10
            )
            
            try:
                response.raise_for_status()
                print(f"✅ Алерт отправлен для {alert_data['symbol']}")
            except requests.exceptions.HTTPError as e:
                print(f"❌ Ошибка отправки в Telegram: {e}")
                print(f"🔍 Детали ошибки: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка отправки в Telegram: {e}")
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
