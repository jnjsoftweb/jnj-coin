import time
from typing import Optional, Dict
from datetime import datetime
from trader.direct import UpbitTrader
from collector.account import UpbitAccount


class TrailingStopTrader:
  def __init__(self):
    self.trader = UpbitTrader()
    self.account = UpbitAccount()

  def trailing_stop(self,
                   symbol: str,
                   trail_percent: float,
                   check_interval: float = 1.0,
                   quantity: Optional[float] = None,
                   initial_price: Optional[float] = None) -> Dict:
    """
    Trailing Stop 매매 실행
    :param symbol: 거래쌍 (예: 'BTC/KRW')
    :param trail_percent: 고점 대비 하락 허용 비율 (예: 1.0 = 1%)
    :param check_interval: 가격 체크 간격 (초)
    :param quantity: 매도할 수량 (None인 경우 전량 매도)
    :param initial_price: 시작 가격 (None인 경우 현재가로 설정)
    :return: 매도 결과
    """
    try:
      # 초기 설정
      if initial_price is None:
        ticker = self.trader.exchange.fetch_ticker(symbol)
        initial_price = ticker['last']

      if quantity is None:
        balances = self.account.get_balances()
        for balance in balances:
          if balance['currency'] == symbol.split('/')[0]:
            quantity = balance['free']
            break
        if quantity is None:
          raise ValueError(f"보유한 {symbol.split('/')[0]}가 없습니다.")

      # Trailing Stop 로직 시작
      highest_price = initial_price
      stop_price = initial_price * (1 - trail_percent / 100)

      print(f"\n[{datetime.now()}] Trailing Stop 시작")
      print(f"초기 가격: {initial_price}")
      print(f"초기 Stop 가격: {stop_price}")
      print(f"매도 수량: {quantity}")

      while True:
        try:
          # 현재가 조회
          ticker = self.trader.exchange.fetch_ticker(symbol)
          current_price = ticker['last']

          # 신규 고점 갱신
          if current_price > highest_price:
            highest_price = current_price
            stop_price = highest_price * (1 - trail_percent / 100)
            print(f"[{datetime.now()}] 신규 고점: {highest_price}, 새로운 Stop 가격: {stop_price}")

          # Stop 조건 확인
          if current_price <= stop_price:
            print(f"\n[{datetime.now()}] Stop 가격 도달! 매도 실행")
            print(f"현재가: {current_price} / Stop 가격: {stop_price}")

            # 매도 주문 실행
            result = self.trader.sell(symbol, quantity, price=None)  # 시장가 매도

            if result:
              print("매도 성공!")
              print(f"매도 수량: {quantity}")
              print(f"매도 가격: {current_price}")
              return result
            else:
              print("매도 실패!")
              return None

          time.sleep(check_interval)

        except Exception as e:
          print(f"가격 조회 중 오류 발생: {str(e)}")
          time.sleep(check_interval)
          continue

    except Exception as e:
      print(f"Trailing Stop 실행 중 오류 발생: {str(e)}")
      return None

  def trailing_buy(self,
                  symbol: str,
                  trail_percent: float,
                  target_amount: float,
                  check_interval: float = 1.0,
                  initial_price: Optional[float] = None) -> Dict:
    """
    Trailing Buy 매매 실행 (하락 추세에서 매수)
    :param symbol: 거래쌍 (예: 'BTC/KRW')
    :param trail_percent: 저점 대비 상승 허용 비율 (예: 1.0 = 1%)
    :param target_amount: 매수할 금액 (KRW)
    :param check_interval: 가격 체크 간격 (초)
    :param initial_price: 시작 가격 (None인 경우 현재가로 설정)
    :return: 매수 결과
    """
    try:
      # 초기 설정
      if initial_price is None:
        ticker = self.trader.exchange.fetch_ticker(symbol)
        initial_price = ticker['last']

      # Trailing Buy 로직 시작
      lowest_price = initial_price
      buy_price = initial_price * (1 + trail_percent / 100)

      print(f"\n[{datetime.now()}] Trailing Buy 시작")
      print(f"초기 가격: {initial_price}")
      print(f"초기 Buy 가격: {buy_price}")
      print(f"매수 금액: {target_amount}")

      while True:
        try:
          # 현재가 조회
          ticker = self.trader.exchange.fetch_ticker(symbol)
          current_price = ticker['last']

          # 신규 저점 갱신
          if current_price < lowest_price:
            lowest_price = current_price
            buy_price = lowest_price * (1 + trail_percent / 100)
            print(f"[{datetime.now()}] 신규 저점: {lowest_price}, 새로운 Buy 가격: {buy_price}")

          # Buy 조건 확인
          if current_price >= buy_price:
            print(f"\n[{datetime.now()}] Buy 가격 도달! 매수 실행")
            print(f"현재가: {current_price} / Buy 가격: {buy_price}")

            # 매수 주문 실행
            result = self.trader.buy(symbol, target_amount, price=None)  # 시장가 매수

            if result:
              print("매수 성공!")
              print(f"매수 금액: {target_amount}")
              print(f"매수 가격: {current_price}")
              return result
            else:
              print("매수 실패!")
              return None

          time.sleep(check_interval)

        except Exception as e:
          print(f"가격 조회 중 오류 발생: {str(e)}")
          time.sleep(check_interval)
          continue

    except Exception as e:
      print(f"Trailing Buy 실행 중 오류 발생: {str(e)}")
      return None


# 사용 예시
if __name__ == "__main__":
  trader = TrailingStopTrader()

  # Trailing Stop 예시 (1% 하락 시 매도)
  # result = trader.trailing_stop(
  #   symbol='CTC/KRW',
  #   trail_percent=1.0,
  #   quantity=100,  # 100 CTC 매도
  #   check_interval=1.0  # 1초마다 체크
  # )

  # Trailing Buy 예시 (1% 상승 시 매수)
  # result = trader.trailing_buy(
  #   symbol='CTC/KRW',
  #   trail_percent=1.0,
  #   target_amount=100000,  # 10만원어치 매수
  #   check_interval=1.0  # 1초마다 체크
  # )
