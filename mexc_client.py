"""
MEXC API клиент для получения данных о фьючерсах
ОПТИМИЗИРОВАНО ДЛЯ МАКСИМАЛЬНОЙ СКОРОСТИ
"""
import requests
import time
from typing import Dict, List, Optional
import config


class MEXCClient:
    def __init__(self):
        self.base_url = config.MEXC_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Выполнить HTTP запрос с повторными попытками"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(config.MAX_RETRIES):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Ошибка запроса (попытка {attempt + 1}/{config.MAX_RETRIES}): {e}")
                if attempt < config.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # Экспоненциальная задержка
                else:
                    return None
        return None
    
    def get_all_futures_symbols(self) -> List[str]:
        """Получить все доступные фьючерсные пары"""
        try:
            data = self._make_request("/api/v1/contract/detail")
            
            if not data or 'data' not in data:
                print("⚠️ Не удалось получить список контрактов")
                return []
            
            symbols = [contract['symbol'] for contract in data['data'] if contract.get('symbol')]
            print(f"✅ Загружено {len(symbols)} фьючерсных пар")
            return symbols
            
        except Exception as e:
            print(f"❌ Ошибка при получении символов: {e}")
            return []
    
    def get_all_tickers(self) -> Dict[str, Dict]:
        """
        ОПТИМИЗИРОВАННЫЙ МЕТОД: Получить ВСЕ тикеры одним запросом!
        Возвращает словарь {symbol: ticker_data}
        """
        try:
            response = self._make_request("/api/v1/contract/ticker")
            
            if not response or not response.get('success') or 'data' not in response:
                print("⚠️ Не удалось получить тикеры")
                return {}
            
            # Преобразуем список тикеров в словарь для быстрого доступа
            tickers = {}
            for ticker in response['data']:
                symbol = ticker.get('symbol')
                if symbol:
                    tickers[symbol] = ticker
            
            return tickers
            
        except Exception as e:
            print(f"❌ Ошибка при получении тикеров: {e}")
            return {}
    
    def get_all_price_data(self) -> List[Dict]:
        """
        СУПЕР БЫСТРЫЙ МЕТОД: Получить все цены одним запросом
        Возвращает список пар с ценовыми данными
        """
        tickers = self.get_all_tickers()
        
        if not tickers:
            return []
        
        price_data_list = []
        
        for symbol, ticker in tickers.items():
            last_price = ticker.get('lastPrice')
            fair_price = ticker.get('fairPrice')
            
            if last_price is None or fair_price is None:
                continue
            
            try:
                last_price = float(last_price)
                fair_price = float(fair_price)
                
                if last_price <= 0 or fair_price <= 0:
                    continue
                
                price_data_list.append({
                    'symbol': symbol,
                    'last_price': last_price,
                    'fair_price': fair_price
                })
            except (ValueError, TypeError):
                continue
        
        return price_data_list

