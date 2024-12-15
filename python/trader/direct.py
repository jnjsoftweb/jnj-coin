from collector.account import UpbitAccount
import os
import ccxt
from dotenv import load_dotenv
from typing import Optional, Dict
import sys
from pathlib import Path

# 프로젝트 루트 경로를 파이썬 path에 추가
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
  sys.path.append(project_root)


# .env 파일 로드
load_dotenv()


class UpbitTrader:
  def __init__(self):
    # Upbit API 인증 정보 설정
    self.exchange = ccxt.upbit({
      'apiKey': os.getenv('UPBIT_ACCESS_KEY'),
      'secret': os.getenv('UPBIT_SECRET_KEY')
    })
    self.account = UpbitAccount()

  def buy(self, symbol: str, amount: float, price: Optional[float] = None):
    """
    매수 주문 (시장가/지정가)
    :param symbol: 거래쌍 (예: 'BTC/KRW')
    :param amount: 매수 수량 또는 금액
    :param price: 매수 희망가격 (None인 경우 시장가 주문)
    :return: 주문 정보
    """
    try:
      if price is None:
        # 시장가 매수
        order = self.exchange.create_market_buy_order(
          symbol=symbol,
          amount=amount,
        )
      else:
        # 지정가 매수
        order = self.exchange.create_limit_buy_order(
          symbol=symbol,
          amount=amount,
          price=price,
        )
      return order
    except Exception as e:
      print(f"매수 주문 실패: {str(e)}")
      return None

  def sell(self, symbol: str, amount: float, price: Optional[float] = None):
    """
    매도 주문 (시장가/지정가)
    :param symbol: 거래쌍 (예: 'BTC/KRW')
    :param amount: 매도할 코인 수량
    :param price: 매도 희망가격 (None인 경우 시장가 주문)
    :return: 주문 정보
    """
    try:
      if price is None:
        # 시장가 매도
        order = self.exchange.create_market_sell_order(
          symbol=symbol,
          amount=amount,
        )
      else:
        # 지정가 매도
        order = self.exchange.create_limit_sell_order(
          symbol=symbol,
          amount=amount,
          price=price,
        )
      return order
    except Exception as e:
      print(f"매도 주문 실패: {str(e)}")
      return None

  def sell_ratio(self, symbol: str, ratio: float, price: Optional[float] = None) -> Dict:
    """
    보유 수량 중 일정 비율만큼 매도
    :param symbol: 거래쌍 (예: 'BTC/KRW')
    :param ratio: 매도 비율 (0.0 ~ 1.0)
    :param price: 매도 희망가격 (None인 경우 시장가 주문)
    :return: 주문 정보
    """
    try:
      if not 0 <= ratio <= 1:
        raise ValueError("ratio는 0과 1 사이의 값이어야 합니다.")

      # 보유 수량 조회
      currency = symbol.split('/')[0]
      balances = self.account.get_balances()
      available_amount = None

      for balance in balances:
        if balance['currency'] == currency:
          available_amount = float(balance['free'])
          break

      if available_amount is None or available_amount == 0:
        raise ValueError(f"보유한 {currency}가 없습니다.")

      # 매도할 수량 계산
      sell_amount = available_amount * ratio

      print(f"매도 비율: {ratio * 100}%")
      print(f"총 보유량: {available_amount} {currency}")
      print(f"매도 수량: {sell_amount} {currency}")

      # 매도 주문 실행
      return self.sell(symbol, sell_amount, price)

    except Exception as e:
      print(f"비율 매도 실패: {str(e)}")
      return None

  def buy_ratio(self, symbol: str, ratio: float, price: Optional[float] = None) -> Dict:
    """
    보유 현금(KRW) 중 일정 비율만큼 매수
    :param symbol: 거래쌍 (예: 'BTC/KRW')
    :param ratio: 매수 비율 (0.0 ~ 1.0)
    :param price: 매수 희망가격 (None인 경우 시장가 주문)
    :return: 주문 정보
    """
    try:
      if not 0 <= ratio <= 1:
        raise ValueError("ratio는 0과 1 사이의 값이어야 합니다.")

      # 보유 KRW 조회
      balances = self.account.get_balances()
      available_krw = None

      for balance in balances:
        if balance['currency'] == 'KRW':
          available_krw = float(balance['free'])
          break

      if available_krw is None or available_krw == 0:
        raise ValueError("보유한 KRW가 없습니다.")

      # 매수할 금액 계산
      buy_amount = available_krw * ratio

      print(f"매수 비율: {ratio * 100}%")
      print(f"사용 가능 KRW: {available_krw:,.0f} KRW")
      print(f"매수 금액: {buy_amount:,.0f} KRW")

      # 매수 주문 실행
      return self.buy(symbol, buy_amount, price)

    except Exception as e:
      print(f"비율 매수 실패: {str(e)}")
      return None


# 사용 예시
if __name__ == "__main__":
  trader = UpbitTrader()

  # 시장가 매수 예시 (1만원어치 BTC 매수)
  # result = trader.buy('BTC/KRW', 10000)

  # 시장가 매도 예시 (0.001 BTC 매도)
  # result = trader.sell('BTC/KRW', 0.001)

  # 지정가 매수 예시 (2000원에 200 XRP 매수)
  # result = trader.buy('XRP/KRW', 200, 2000)
  # print(result)

  # 지정가 매도 예시 (1000만원에 0.1 BTC 매도)
  # result = trader.sell('CTC/KRW', 200, 2600)
  # print(result)

  # 보유 CTC의 20% 2500원에 매도
  result = trader.sell_ratio('CTC/KRW', 0.2, 2500)
  print(result)

  # 매도 주문 실패: upbit {"error":{"message":"주문 가능한 최소금액은 5000KRW 입니다. 시장가 매도 시 주문금액은 주문 수량 * 매수 1호가로 계산합니다.","name":"under_min_total_market_ask"}}
  # None

  # 보유 KRW의 30% 로 시장가 매수
  # result = trader.buy_ratio('CTC/KRW', 0.3)
  # print(result)
