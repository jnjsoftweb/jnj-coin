import time
from typing import Optional, Dict
from datetime import datetime
from trader.direct import UpbitTrader
from collector.account import UpbitAccount


class DipTrader:
  def __init__(self):
    self.trader = UpbitTrader()
    self.account = UpbitAccount()

  def trade_simple(self,
                  symbol: str,
                  target_amount: float,
                  dip_percent: float = 1.0,
                  profit_percent: float = 5.0,
                  loss_percent: float = 3.0,
                  check_interval: float = 1.0) -> Dict:
    """
    단순 딥 매매: 하락 시 매수 후 목표 수익률 도달 또는 손절 시 매도
    :param symbol: 거래쌍 (예: 'BTC/KRW')
    :param target_amount: 매수할 금액 (KRW)
    :param dip_percent: 매수 진입 기준 하락률 (예: 1.0 = 1%)
    :param profit_percent: 목표 수익률 (예: 5.0 = 5%)
    :param loss_percent: 손절 기준 하락률 (예: 3.0 = 3%)
    :param check_interval: 가격 체크 간격 (초)
    :return: 매도 결과
    """
    try:
      # 초기 가격 설정
      ticker = self.trader.exchange.fetch_ticker(symbol)
      initial_price = ticker['last']
      buy_price = initial_price * (1 - dip_percent / 100)  # 매수 목표가
      
      print(f"\n[{datetime.now()}] 딥 매매 시작")
      print(f"현재 가격: {initial_price}")
      print(f"매수 목표가: {buy_price} ({dip_percent}% 하락 시)")
      
      # 매수 대기
      while True:
        try:
          ticker = self.trader.exchange.fetch_ticker(symbol)
          current_price = ticker['last']
          
          # 매수 조건 확인
          if current_price <= buy_price:
            print(f"\n[{datetime.now()}] 매수 목표가 도달! 매수 실행")
            print(f"현재가: {current_price}")
            
            # 매수 실행
            buy_result = self.trader.buy(symbol, target_amount, price=None)
            if not buy_result:
              print("매수 실패!")
              return None
            
            buy_price = current_price  # 실제 매수 가격 저장
            sell_profit_price = buy_price * (1 + profit_percent / 100)  # 익절가
            sell_loss_price = buy_price * (1 - loss_percent / 100)    # 손절가
            
            print("매수 성공!")
            print(f"매수 가격: {buy_price}")
            print(f"익절 목표가: {sell_profit_price} (+{profit_percent}%)")
            print(f"손절 목표가: {sell_loss_price} (-{loss_percent}%)")
            
            # 매도 대기
            while True:
              ticker = self.trader.exchange.fetch_ticker(symbol)
              current_price = ticker['last']
              
              # 익절 또는 손절 조건 확인
              if current_price >= sell_profit_price or current_price <= sell_loss_price:
                print(f"\n[{datetime.now()}] 매도 조건 도달! 매도 실행")
                print(f"현재가: {current_price}")
                
                # 매도 수량 계산 (매수한 수량)
                quantity = float(buy_result['amount'])
                
                # 매도 실행
                sell_result = self.trader.sell(symbol, quantity, price=None)
                if sell_result:
                  profit_percent_actual = ((current_price - buy_price) / buy_price) * 100
                  print("매도 성공!")
                  print(f"매도 가격: {current_price}")
                  print(f"수익률: {profit_percent_actual:.2f}%")
                  return sell_result
                else:
                  print("매도 실패!")
                  return None
              
              time.sleep(check_interval)
              
        except Exception as e:
          print(f"가격 조��� 중 오류 발생: {str(e)}")
          time.sleep(check_interval)
          continue
          
    except Exception as e:
      print(f"딥 매매 실행 중 오류 발생: {str(e)}")
      return None

  def trade_trailing(self,
                    symbol: str,
                    target_amount: float,
                    dip_percent: float = 1.0,
                    profit_percent: float = 5.0,
                    loss_percent: float = 3.0,
                    trailing_percent: float = 1.0,
                    check_interval: float = 1.0) -> Dict:
    """
    Trailing Stop을 활용한 딥 매매
    :param symbol: 거래쌍 (예: 'BTC/KRW')
    :param target_amount: 매수할 금액 (KRW)
    :param dip_percent: 매수 진입 기준 하락률 (예: 1.0 = 1%)
    :param profit_percent: 초기 목표 수익률 (예: 5.0 = 5%)
    :param loss_percent: 손절 기준 하락률 (예: 3.0 = 3%)
    :param trailing_percent: Trailing Stop 기준 하락률 (예: 1.0 = 1%)
    :param check_interval: 가격 체크 간격 (초)
    :return: 매도 결과
    """
    try:
      # 초기 가격 설정
      ticker = self.trader.exchange.fetch_ticker(symbol)
      initial_price = ticker['last']
      buy_price = initial_price * (1 - dip_percent / 100)  # 매수 목표가
      
      print(f"\n[{datetime.now()}] Trailing 딥 매매 시작")
      print(f"현재 가격: {initial_price}")
      print(f"매수 목표가: {buy_price} ({dip_percent}% 하락 시)")
      
      # 매수 대기
      while True:
        try:
          ticker = self.trader.exchange.fetch_ticker(symbol)
          current_price = ticker['last']
          
          # 매수 조건 확인
          if current_price <= buy_price:
            print(f"\n[{datetime.now()}] 매수 목표가 도달! 매수 실행")
            print(f"현재가: {current_price}")
            
            # 매수 실행
            buy_result = self.trader.buy(symbol, target_amount, price=None)
            if not buy_result:
              print("매수 실패!")
              return None
            
            buy_price = current_price  # 실제 매수 가격 저장
            highest_price = buy_price  # Trailing Stop을 위한 고점 가격
            sell_profit_price = buy_price * (1 + profit_percent / 100)  # 초기 익절가
            sell_loss_price = buy_price * (1 - loss_percent / 100)    # 손절가
            trailing_stop_price = highest_price * (1 - trailing_percent / 100)  # Trailing Stop 가격
            
            print("매수 성공!")
            print(f"매수 가격: {buy_price}")
            print(f"익절 목표가: {sell_profit_price} (+{profit_percent}%)")
            print(f"손절 목표가: {sell_loss_price} (-{loss_percent}%)")
            print(f"Trailing Stop 가격: {trailing_stop_price}")
            
            # 매도 대기
            while True:
              ticker = self.trader.exchange.fetch_ticker(symbol)
              current_price = ticker['last']
              
              # 고점 갱신 시 Trailing Stop 가격 수정
              if current_price > highest_price:
                highest_price = current_price
                trailing_stop_price = highest_price * (1 - trailing_percent / 100)
                print(f"[{datetime.now()}] 신규 고점: {highest_price}, Trailing Stop 가격: {trailing_stop_price}")
              
              # 익절, 손절, 또는 Trailing Stop 조건 확인
              if (current_price >= sell_profit_price or 
                  current_price <= sell_loss_price or 
                  (current_price > buy_price and current_price <= trailing_stop_price)):
                
                print(f"\n[{datetime.now()}] 매도 조건 도달! 매도 실행")
                print(f"현재가: {current_price}")
                
                # 매도 수량 계산 (매수한 수량)
                quantity = float(buy_result['amount'])
                
                # 매도 실행
                sell_result = self.trader.sell(symbol, quantity, price=None)
                if sell_result:
                  profit_percent_actual = ((current_price - buy_price) / buy_price) * 100
                  print("매도 성공!")
                  print(f"매도 가격: {current_price}")
                  print(f"수익률: {profit_percent_actual:.2f}%")
                  return sell_result
                else:
                  print("매도 실패!")
                  return None
              
              time.sleep(check_interval)
              
        except Exception as e:
          print(f"가격 조회 중 오류 발생: {str(e)}")
          time.sleep(check_interval)
          continue
          
    except Exception as e:
      print(f"Trailing 딥 매매 실행 중 오류 발생: {str(e)}")
      return None


# 사용 예시
if __name__ == "__main__":
  trader = DipTrader()
  
  # 단순 딥 매매 예시
  # result = trader.trade_simple(
  #   symbol='CTC/KRW',
  #   target_amount=100000,  # 10만원어치
  #   dip_percent=1.0,      # 1% 하락 시 매수
  #   profit_percent=5.0,   # 5% 상승 시 매도
  #   loss_percent=3.0,     # 3% 하락 시 손절
  #   check_interval=1.0    # 1초마다 체크
  # )
  
  # Trailing Stop 딥 매매 예시
  # result = trader.trade_trailing(
  #   symbol='CTC/KRW',
  #   target_amount=100000,    # 10만원어치
  #   dip_percent=1.0,        # 1% 하락 시 매수
  #   profit_percent=5.0,     # 5% 상승 시 매도
  #   loss_percent=3.0,       # 3% 하락 시 손절
  #   trailing_percent=1.0,   # 고점 대비 1% 하락 시 매도
  #   check_interval=1.0      # 1초마다 체크
  # )
