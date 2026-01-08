"""
MEXC Price Spread Monitor - Главный модуль
Мониторинг разницы между последней ценой и справедливой ценой на фьючерсах MEXC
"""
import time
import sys
from datetime import datetime
from mexc_client import MEXCClient
from spread_analyzer import SpreadAnalyzer
from telegram_notifier import TelegramNotifier
import config


class PriceSpreadMonitor:
    def __init__(self):
        print("🚀 Инициализация MEXC Price Spread Monitor...")
        
        try:
            self.mexc = MEXCClient()
            self.analyzer = SpreadAnalyzer()
            self.notifier = TelegramNotifier()
            print("✅ Все компоненты инициализированы")
        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            sys.exit(1)
        
        self.symbols = []
        self.is_running = False
        self.scan_counter = 0  # Счётчик сканирований
        self.total_alerts = 0  # Общее количество алертов
    
    def load_symbols(self):
        """Загрузить все фьючерсные пары"""
        print("\n📥 Загрузка списка фьючерсных пар...")
        self.symbols = self.mexc.get_all_futures_symbols()
        
        if not self.symbols:
            print("❌ Не удалось загрузить символы. Повторная попытка через 30 секунд...")
            return False
        
        print(f"✅ Загружено {len(self.symbols)} пар для мониторинга")
        
        # Показываем примеры пар с ценами при запуске
        print("\n📊 Получение примеров цен для проверки...")
        sample_data = self.mexc.get_all_price_data()
        
        if sample_data:
            print(f"✅ Данные получены для {len(sample_data)} пар\n")
            print("📋 Примеры пар с текущими ценами:")
            print("-" * 70)
            
            # Показываем первые 10 пар
            for i, data in enumerate(sample_data[:10], 1):
                symbol = data['symbol']
                last = data['last_price']
                fair = data['fair_price']
                diff = ((last - fair) / fair) * 100
                
                print(f"{i:2d}. {symbol:15s} | Last: {last:12.6f} | Fair: {fair:12.6f} | Δ {diff:+6.2f}%")
            
            print("-" * 70)
            print(f"... и ещё {len(sample_data) - 10} пар\n")
        
        return True
    
    def scan_all_pairs(self):
        """Сканировать все пары на наличие спреда - ОПТИМИЗИРОВАННАЯ ВЕРСИЯ"""
        self.scan_counter += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # СУПЕР БЫСТРО: Получаем ВСЕ тикеры одним запросом!
        all_price_data = self.mexc.get_all_price_data()
        
        if not all_price_data:
            print(f"[{timestamp}] ❌ Ошибка получения данных")
            return
        
        alerts_sent = 0
        max_spread = 0
        max_spread_pair = None
        
        for price_data in all_price_data:
            try:
                # Анализируем спред
                alert_data = self.analyzer.analyze(price_data)
                
                # Отслеживаем максимальный спред
                spread = abs(((price_data['last_price'] - price_data['fair_price']) / price_data['fair_price']) * 100)
                if spread > max_spread:
                    max_spread = spread
                    max_spread_pair = price_data['symbol']
                
                if alert_data:
                    # Очищаем строку и выводим алерт
                    print(f"\n{'='*70}")
                    print(f"🚨 СПРЕД ОБНАРУЖЕН: {alert_data['symbol']}")
                    print(f"{'='*70}")
                    print(f"💰 Последняя цена:    {alert_data['last_price']:12.6f}")
                    print(f"⚖️  Справедливая цена: {alert_data['fair_price']:12.6f}")
                    print(f"📈 Разница:           {alert_data['spread_percent']:+6.2f}% ({alert_data['direction']} справедливой)")
                    print(f"⏰ Время обнаружения: {timestamp}")
                    print(f"{'='*70}\n")
                    
                    # Отправляем уведомление
                    self.notifier.send_alert_sync(alert_data)
                    alerts_sent += 1
                    self.total_alerts += 1
                
            except Exception as e:
                continue
        
        # Компактный лог - одна строка
        if alerts_sent > 0:
            print(f"[{timestamp}] Скан #{self.scan_counter}: ✅ {len(all_price_data)} пар | 🔔 АЛЕРТОВ: {alerts_sent} | Всего: {self.total_alerts}")
        else:
            # Показываем только каждое 10-е сканирование если нет алертов
            if self.scan_counter % 10 == 0:
                print(f"[{timestamp}] Скан #{self.scan_counter}: ✅ {len(all_price_data)} пар | Макс спред: {max_spread:.2f}% ({max_spread_pair})") 
    
    def run(self):
        """Основной цикл мониторинга"""
        print("\n" + "="*70)
        print("MEXC PRICE SPREAD MONITOR - МАКСИМАЛЬНАЯ СКОРОСТЬ")
        print("="*70)
        print(f"Минимальный спред: {config.MIN_SPREAD_PERCENT}%")
        print(f"Режим: НЕПРЕРЫВНОЕ СКАНИРОВАНИЕ (без задержек)")
        print(f"Cooldown между алертами: {config.ALERT_COOLDOWN} сек")
        print("="*70 + "\n")
        
        # Загружаем список символов
        while not self.load_symbols():
            time.sleep(30)
        
        self.is_running = True
        print("✅ Мониторинг запущен! Нажмите Ctrl+C для остановки")
        print(f"⏱️  Интервал сканирования: {config.SCAN_INTERVAL} сек")
        print("📊 Показываю каждое 10-е сканирование (или сразу при обнаружении алерта)\n")
        
        try:
            while self.is_running:
                self.scan_all_pairs()
                time.sleep(config.SCAN_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Получен сигнал остановки...")
            print(f"📊 Статистика: выполнено {self.scan_counter} сканирований, отправлено {self.total_alerts} алертов")
            self.stop()
    
    def stop(self):
        """Остановить мониторинг"""
        self.is_running = False
        print("✅ Мониторинг остановлен")


if __name__ == "__main__":
    monitor = PriceSpreadMonitor()
    monitor.run()
