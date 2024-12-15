import ccxt
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class UpbitChart:
  def __init__(self):
    self.exchange = ccxt.upbit({
      'apiKey': os.getenv('UPBIT_ACCESS_KEY'),
      'secret': os.getenv('UPBIT_SECRET_KEY')
    })

  def get_ohlcv(self, symbol='BTC/KRW', timeframe='1d', limit=100):
    """
    OHLCV 데이터 조회
    :param symbol: 거래쌍 (예: 'BTC/KRW')
    :param timeframe: 시간단위 ('1m', '1h', '1d' 등)
    :param limit: 조회할 캔들 개수
    :return: DataFrame
    """
    try:
      ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
      df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
      df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
      return df
    except Exception as e:
      print(f"OHLCV 데이터 조회 실패: {str(e)}")
      return None

  def get_orderbook(self, symbol='BTC/KRW'):
    """
    호가창 데이터 조회
    :param symbol: 거래쌍 (예: 'BTC/KRW')
    :return: Dictionary
    """
    try:
      orderbook = self.exchange.fetch_order_book(symbol)
      return {
        'timestamp': datetime.fromtimestamp(orderbook['timestamp']/1000),
        'bids': orderbook['bids'],  # [[가격, 수량], ...]
        'asks': orderbook['asks']   # [[가격, 수량], ...]
      }
    except Exception as e:
      print(f"호가창 데이터 조회 실패: {str(e)}")
      return None

  def get_balance(self):
    """
    잔고 조회
    :return: Dictionary
    """
    try:
      balance = self.exchange.fetch_balance()
      # 보유 중인 자산만 필터링
      holdings = {}
      for currency in balance['total']:
        if balance['total'][currency] > 0:
          holdings[currency] = {
            'free': balance['free'][currency],
            'used': balance['used'][currency],
            'total': balance['total'][currency]
          }
      return holdings
    except Exception as e:
      print(f"잔고 조회 실패: {str(e)}")
      return None

# 사용 예시
if __name__ == "__main__":
  collector = UpbitChart()
  
  # OHLCV 데이터 조회
  ohlcv = collector.get_ohlcv(timeframe='1h', limit=24)  # 최근 24시간 데이터
  print("\n=== OHLCV 데이터 ===")
  print(ohlcv)
  
  # 호가창 데이터 조회
  orderbook = collector.get_orderbook()
  print("\n=== 호가창 데이터 ===")
  print(orderbook)
  
  # 잔고 조회
  balance = collector.get_balance()
  print("\n=== 잔고 데이터 ===")
  if balance:
    for currency, data in balance.items():
      print(f"{currency}: {data}")
