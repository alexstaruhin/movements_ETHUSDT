import pandas as pd
import requests
import json
import time


def get_data():

# Загрузить исторические данные ETHUSDT и BTCUSDT за последний час
    symbol_eth = 'ETHUSDT'
    symbol_btc = 'BTCUSDT'
    interval = '1m'

# количество свечей за последний час
    limit = 60
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol_eth}&interval={interval}&limit={limit}'
    response_eth = requests.get(url)
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol_btc}&interval={interval}&limit={limit}'
    response_btc = requests.get(url)
    data_eth = json.loads(response_eth.text)
    data_btc = json.loads(response_btc.text)
    prices_eth = pd.DataFrame(data_eth, dtype=float)
    prices_btc = pd.DataFrame(data_btc, dtype=float)
    prices_eth = prices_eth.iloc[:,:6]
    prices_btc = prices_btc.iloc[:,:6]
    columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    prices_eth.columns = columns
    prices_btc.columns = columns
    prices_eth['time'] = pd.to_datetime(prices_eth['time'], unit='ms')
    prices_btc['time'] = pd.to_datetime(prices_btc['time'], unit='ms')
    prices_eth = prices_eth.set_index('time')
    prices_btc = prices_btc.set_index('time')

    return prices_eth, prices_btc


def price_action_of_futures_eth(prices_eth, prices_btc):

# Рассчитать спред между ценами ETHUSDT и BTCUSDT для каждого момента времени
    spread = prices_eth['close'] - prices_btc['close']

# Определить скользящее среднее спреда за последние 60 минут
    rolling_mean = spread.rolling('60min').mean()

# Вычесть скользящее среднее спреда из текущего значения спреда
    spread_adj = spread - rolling_mean

# Вычислить собственные движения цены фьючерса ETHUSDT
    eth_futures_movements = prices_eth['close'] - spread_adj

    return eth_futures_movements


while True:

# Функция получения данных за последний час с интервалом 1 минута
    prices_eth, prices_btc = get_data()

# Функция определения собственных движений цены фьючерса ETHUSDT, исключив из них движения вызванные влиянием цены BTCUSDT
    eth_df = price_action_of_futures_eth(prices_eth, prices_btc)

# Поиск изменения цены за последний час отнисительно максимального и минимального значения цены
    change_min = (eth_df[len(eth_df) - 1] - min(eth_df)) / min(eth_df)
    change_max = (max(eth_df) - eth_df[len(eth_df) - 1]) / max(eth_df)

# Нахождение максимального изменения цены за последний час
    change_all = max(change_min, change_max)

# Вывод сообщения в консоль при условии изменения цены на 1%
    if change_all >= 0.01:
        print(f'Цена фьючерса ETHUSDT изменилась на {round(change_all * 100, 2)} %')

# Минутная задержка цикла
    time.sleep(60)