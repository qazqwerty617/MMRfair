"""
Анализатор спреда между последней ценой и справедливой ценой
УМНЫЙ COOLDOWN: разные токены = нет cooldown, один токен = 5 мин или +5% спред
"""
import time
from typing import Dict, Optional
import config


class SpreadAnalyzer:
    def __init__(self):
        # Хранит {symbol: {'timestamp': float, 'spread': float}}
        self.alert_history: Dict[str, Dict] = {}
    
    def calculate_spread_percent(self, last_price: float, fair_price: float) -> float:
        """Рассчитать процент разницы между последней и справедливой ценой"""
        if fair_price == 0:
            return 0.0
        
        spread = ((last_price - fair_price) / fair_price) * 100
        return spread
    
    def should_alert(self, symbol: str, spread_percent: float) -> bool:
        """
        Проверить, нужно ли отправлять алерт
        
        Логика:
        - Разные токены: нет cooldown (всегда отправляем)
        - Один токен: cooldown 5 минут ИЛИ если спред вырос на +5%
        """
        # Проверяем минимальный порог
        if abs(spread_percent) < config.MIN_SPREAD_PERCENT:
            return False
        
        # Если этот символ еще не был в истории - отправляем алерт
        if symbol not in self.alert_history:
            return True
        
        # Получаем данные предыдущего алерта
        last_alert = self.alert_history[symbol]
        last_timestamp = last_alert['timestamp']
        last_spread = last_alert['spread']
        
        current_time = time.time()
        time_passed = current_time - last_timestamp
        
        # Проверяем cooldown
        if time_passed < config.ALERT_COOLDOWN:
            # Cooldown еще активен - проверяем изменение спреда
            spread_increase = abs(spread_percent) - abs(last_spread)
            
            if spread_increase >= 5.0:  # Спред вырос на 5%+
                print(f"   💡 {symbol}: Спред вырос на {spread_increase:.2f}% (было {abs(last_spread):.2f}%, стало {abs(spread_percent):.2f}%)")
                return True
            else:
                # Cooldown активен и спред не вырос значительно
                return False
        
        # Cooldown прошел - можно отправлять
        return True
    
    def mark_alerted(self, symbol: str, spread_percent: float):
        """Отметить, что алерт был отправлен"""
        self.alert_history[symbol] = {
            'timestamp': time.time(),
            'spread': spread_percent
        }
    
    def analyze(self, price_data: Dict) -> Optional[Dict]:
        """Проанализировать данные о ценах и вернуть результат, если нужен алерт"""
        symbol = price_data['symbol']
        last_price = price_data['last_price']
        fair_price = price_data['fair_price']
        
        spread_percent = self.calculate_spread_percent(last_price, fair_price)
        
        if self.should_alert(symbol, spread_percent):
            self.mark_alerted(symbol, spread_percent)
            
            return {
                'symbol': symbol,
                'last_price': last_price,
                'fair_price': fair_price,
                'spread_percent': spread_percent,
                'direction': 'выше' if spread_percent > 0 else 'ниже'
            }
        
        return None
