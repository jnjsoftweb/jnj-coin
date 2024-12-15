import os
import ccxt
from dotenv import load_dotenv
from typing import Optional, Dict, List

# .env 파일 로드
load_dotenv()

class UpbitAccount:
  def __init__(self):
    self.exchange = ccxt.upbit({
      'apiKey': os.getenv('UPBIT_ACCESS_KEY'),
      'secret': os.getenv('UPBIT_SECRET_KEY')
    })

  def get_balances(self) -> List[Dict]:
    """
    전체 보유 자산 조회
    :return: 보유 자산 목록
    """
    try:
      balances = self.exchange.fetch_balance()
      # 잔액이 있는 자산만 필터링
      result = []
      for currency in balances['total'].keys():
        if float(balances['total'][currency]) > 0:
          result.append({
            'currency': currency,
            'free': float(balances['free'][currency]),
            'used': float(balances['used'][currency]),
            'total': float(balances['total'][currency])
          })
      return result
    except Exception as e:
      print(f"잔액 조회 실패: {str(e)}")
      return []

  def get_orders(self, symbol: Optional[str] = None, limit: int = 100) -> List[Dict]:
    """
    주문 내역 조회 (closed orders)
    :param symbol: 거래쌍 (예: 'BTC/KRW'), None이면 전체 조회
    :param limit: 조회할 주문 개수
    :return: 주문 목록
    """
    try:
      if symbol:
        orders = self.exchange.fetch_closed_orders(symbol=symbol, limit=limit)
      else:
        # Upbit는 전체 주문 조회가 지원되지 않으므로 빈 리스트 반환
        print("Upbit는 전체 주문 조회를 지원하지 않습니다. 심볼을 지정해주세요.")
        return []
      return orders
    except Exception as e:
      print(f"주문 내역 조회 실패: {str(e)}")
      return []

  def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
    """
    미체결 주문 조회
    :param symbol: 거래쌍 (예: 'BTC/KRW'), None이면 전체 조회
    :return: 미체결 주문 목록
    """
    try:
      if symbol:
        orders = self.exchange.fetch_open_orders(symbol=symbol)
      else:
        # Upbit는 전체 미체결 주문 조회 지원
        orders = self.exchange.fetch_open_orders()
      return orders
    except Exception as e:
      print(f"미체결 주문 조회 실패: {str(e)}")
      return []

  def get_order_status(self, order_id: str, symbol: str) -> Dict:
    """
    특정 주문의 상태 조회
    :param order_id: 주문 ID
    :param symbol: 거래쌍 (예: 'BTC/KRW')
    :return: 주문 정보
    """
    try:
      order = self.exchange.fetch_order(order_id, symbol)
      return order
    except Exception as e:
      print(f"주문 상태 조회 실패: {str(e)}")
      return {}

  def cancel_order(self, order_id: str, symbol: str) -> Dict:
    """
    주문 취소
    :param order_id: 취소할 주문 ID
    :param symbol: 거래쌍 (예: 'BTC/KRW')
    :return: 취소 결과
    """
    try:
      result = self.exchange.cancel_order(order_id, symbol)
      return result
    except Exception as e:
      print(f"주문 취소 실패: {str(e)}")
      return {}

# 사용 예시
if __name__ == "__main__":
  account = UpbitAccount()
  
  # 보유 자산 조회
  balances = account.get_balances()
  print("\n보유 자산:")
  for balance in balances:
    print(f"{balance['currency']}: {balance['total']} (사용 가능: {balance['free']}, 주문 중: {balance['used']})")
  
  # 미체결 주문 조회
  symbol = 'CTC/KRW'
  open_orders = account.get_open_orders(symbol)
  print(f"\n{symbol} 미체결 주문:")
  for order in open_orders:
    print(f"주문 ID: {order['id']}, 가격: {order['price']}, 수량: {order['amount']}, 타입: {order['type']}")
  
  # 완료된 주문 조회
  closed_orders = account.get_orders(symbol)
  print(f"\n{symbol} 완료된 주문:")
  for order in closed_orders:
    print(f"주문 ID: {order['id']}, 가격: {order['price']}, 수량: {order['amount']}, 상태: {order['status']}")
