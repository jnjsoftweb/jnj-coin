from trader.direct import UpbitTrader

def test_sell_ctc():
  try:
    # UpbitTrader 인스턴스 생성
    trader = UpbitTrader()
    
    # CTC 200개를 2600원에 지정가 매도
    result = trader.sell('CTC/KRW', 30, 2500)
    
    if result:
      print("주문 성공:")
      print(f"주문 ID: {result['id']}")
      print(f"주문 상태: {result['status']}")
      print(f"주문 가격: {result['price']}")
      print(f"주문 수량: {result['amount']}")
    else:
      print("주문 실패")
      
  except Exception as e:
    print(f"에러 발생: {str(e)}")

if __name__ == "__main__":
  test_sell_ctc()


  # 매도 주문 실패: upbit {"error":{"name":"insufficient_funds_ask","message":"주문가능한 금액(CTC)이 부족합니다."}}