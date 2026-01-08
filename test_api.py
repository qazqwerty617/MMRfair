"""
Тестовый скрипт для проверки MEXC API
"""
import requests
import json

base_url = "https://contract.mexc.com"

# Тест 1: Получить список контрактов
print("=" * 60)
print("ТЕСТ 1: Получение списка контрактов")
print("=" * 60)
response = requests.get(f"{base_url}/api/v1/contract/detail")
data = response.json()
print(f"Статус: {response.status_code}")
print(f"Количество контрактов: {len(data.get('data', []))}")
if data.get('data'):
    print(f"\nПример первого контракта:")
    print(json.dumps(data['data'][0], indent=2, ensure_ascii=False))

# Тест 2: Получить тикер для BTC_USDT
print("\n" + "=" * 60)
print("ТЕСТ 2: Получение тикера BTC_USDT")
print("=" * 60)
response = requests.get(f"{base_url}/api/v1/contract/ticker", params={'symbol': 'BTC_USDT'})
data = response.json()
print(f"Статус: {response.status_code}")
print(f"Ответ:")
print(json.dumps(data, indent=2, ensure_ascii=False))

# Тест 3: Получить fair price для BTC_USDT
print("\n" + "=" * 60)
print("ТЕСТ 3: Получение fair price BTC_USDT")
print("=" * 60)
response = requests.get(f"{base_url}/api/v1/contract/fair_price/BTC_USDT")
data = response.json()
print(f"Статус: {response.status_code}")
print(f"Ответ:")
print(json.dumps(data, indent=2, ensure_ascii=False))

# Тест 4: Альтернативный endpoint для тикера (без параметров)
print("\n" + "=" * 60)
print("ТЕСТ 4: Получение всех тикеров")
print("=" * 60)
response = requests.get(f"{base_url}/api/v1/contract/ticker")
data = response.json()
print(f"Статус: {response.status_code}")
if data.get('data'):
    print(f"Количество тикеров: {len(data.get('data', []))}")
    # Найти BTC_USDT
    btc_ticker = next((t for t in data.get('data', []) if t.get('symbol') == 'BTC_USDT'), None)
    if btc_ticker:
        print(f"\nBTC_USDT тикер:")
        print(json.dumps(btc_ticker, indent=2, ensure_ascii=False))
