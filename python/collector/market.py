import os
import ccxt
from dotenv import load_dotenv
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

# .env 파일 로드
load_dotenv()

class UpbitMarket:
  def __init__(self):
    self.exchange = ccxt.upbit({
      'apiKey': os.getenv('UPBIT_ACCESS_KEY'),
      'secret': os.getenv('UPBIT_SECRET_KEY')
    })

  def get_market_trend(self, timeframe: str = '1d', min_volume_krw: float = 1000000000) -> Dict:
    """
    시장 전반적인 트렌드 분석
    :param timeframe: 기간 (1m, 5m, 15m, 1h, 4h, 1d)
    :param min_volume_krw: 최소 거래대금 (KRW)
    :return: 시장 동향 정보
    """
    try:
      # KRW 마켓의 모든 티커 조회
      tickers = self.exchange.fetch_tickers()
      krw_tickers = {k: v for k, v in tickers.items() if k.endswith('/KRW')}
      
      # 상승/하락/보합 카운트
      up_count = 0
      down_count = 0
      stable_count = 0
      
      # 거래량 상위 코인 저장
      volume_ranking = []
      
      # 가격 변동률 상/하위 코인 저장
      change_ranking = []
      
      for symbol, ticker in krw_tickers.items():
        # 최소 거래대금 필터링
        if float(ticker['quoteVolume'] or 0) < min_volume_krw:
          continue
          
        change_percent = float(ticker['percentage'] or 0)
        volume_krw = float(ticker['quoteVolume'] or 0)
        
        # 상승/하락/보합 카운트
        if change_percent > 0.5:  # 0.5% 이상 상승
          up_count += 1
        elif change_percent < -0.5:  # 0.5% 이상 하락
          down_count += 1
        else:
          stable_count += 1
          
        # 거래량 랭킹을 위해 저장
        volume_ranking.append({
          'symbol': symbol,
          'volume': volume_krw,
          'change': change_percent,
          'price': ticker['last']
        })
        
        # 가격 변동률 랭킹을 위해 저장
        change_ranking.append({
          'symbol': symbol,
          'change': change_percent,
          'volume': volume_krw,
          'price': ticker['last']
        })
      
      # 거래량 기준 정렬
      volume_ranking.sort(key=lambda x: x['volume'], reverse=True)
      
      # 가격 변동률 기준 정렬
      change_ranking.sort(key=lambda x: x['change'], reverse=True)
      
      # 시장 상태 판단
      total_coins = up_count + down_count + stable_count
      market_state = "상승" if up_count > down_count else "하락" if down_count > up_count else "보합"
      
      return {
        'market_state': market_state,
        'statistics': {
          'total_coins': total_coins,
          'up_coins': up_count,
          'down_coins': down_count,
          'stable_coins': stable_count,
          'up_ratio': round(up_count / total_coins * 100, 2),
          'down_ratio': round(down_count / total_coins * 100, 2),
          'stable_ratio': round(stable_count / total_coins * 100, 2)
        },
        'volume_top5': volume_ranking[:5],
        'change_top5': change_ranking[:5],
        'change_bottom5': change_ranking[-5:][::-1],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      }
      
    except Exception as e:
      print(f"시장 동향 분석 중 오류 발생: {str(e)}")
      return {}

  def get_market_dominance(self) -> List[Dict]:
    """
    시가총액 기준 시장 지배력 계산
    :return: 코인별 시장 지배력 정보
    """
    try:
      tickers = self.exchange.fetch_tickers()
      krw_tickers = {k: v for k, v in tickers.items() if k.endswith('/KRW')}
      
      # 시가총액 계산 (현재가 * 거래량)
      market_caps = []
      total_market_cap = 0
      
      for symbol, ticker in krw_tickers.items():
        market_cap = float(ticker['last'] or 0) * float(ticker['baseVolume'] or 0)
        if market_cap > 0:
          market_caps.append({
            'symbol': symbol,
            'market_cap': market_cap
          })
          total_market_cap += market_cap
      
      # 시장 지배력 계산 및 정렬
      dominance = []
      for coin in market_caps:
        dominance.append({
          'symbol': coin['symbol'],
          'market_cap': coin['market_cap'],
          'dominance': round(coin['market_cap'] / total_market_cap * 100, 2)
        })
      
      return sorted(dominance, key=lambda x: x['dominance'], reverse=True)[:10]
      
    except Exception as e:
      print(f"시장 지배력 계산 중 오류 발생: {str(e)}")
      return []

  def print_market_summary(self):
    """
    시장 동향 요약 출력
    """
    trend = self.get_market_trend()
    dominance = self.get_market_dominance()
    
    print("\n=== 업비트 시장 동향 요약 ===")
    print(f"분석 시각: {trend['timestamp']}")
    print(f"\n시장 상태: {trend['market_state']}")
    
    stats = trend['statistics']
    print(f"\n코인 상승/하락 비율:")
    print(f"상승: {stats['up_coins']}개 ({stats['up_ratio']}%)")
    print(f"하락: {stats['down_coins']}개 ({stats['down_ratio']}%)")
    print(f"보합: {stats['stable_coins']}개 ({stats['stable_ratio']}%)")
    
    print("\n거래대금 상위 5:")
    for coin in trend['volume_top5']:
      print(f"{coin['symbol']}: {coin['volume']:,.0f}원 (변동률: {coin['change']}%)")
    
    print("\n상승률 상위 5:")
    for coin in trend['change_top5']:
      print(f"{coin['symbol']}: {coin['change']}% (거래대금: {coin['volume']:,.0f}원)")
    
    print("\n하락률 상위 5:")
    for coin in trend['change_bottom5']:
      print(f"{coin['symbol']}: {coin['change']}% (거래대금: {coin['volume']:,.0f}원)")
    
    print("\n시가총액 점유율 상위 10:")
    for coin in dominance:
      print(f"{coin['symbol']}: {coin['dominance']}%")

  def get_trading_signals(self, recommend_count: int = 5, min_volume_krw: float = 1000000000) -> Dict:
    """
    현재 시장 상황을 분석하여 매수/매도 추천 코인 선별
    :param recommend_count: 추천할 코인 개수
    :param min_volume_krw: 최소 거래대금 (KRW)
    :return: 매수/매도 추천 정보
    """
    try:
      tickers = self.exchange.fetch_tickers()
      krw_tickers = {k: v for k, v in tickers.items() if k.endswith('/KRW')}
      
      # 분석을 위한 코인 데이터 수집
      coin_data = []
      for symbol, ticker in krw_tickers.items():
        volume = float(ticker['quoteVolume'] or 0)
        if volume < min_volume_krw:
          continue
          
        # 기본 정보 수집
        change_24h = float(ticker['percentage'] or 0)
        last_price = float(ticker['last'] or 0)
        
        # RSI 계산을 위한 OHLCV 데이터 조회 (4시간 기준)
        ohlcv = self.exchange.fetch_ohlcv(symbol, '4h', limit=14)
        if not ohlcv:
          continue
          
        # RSI 계산
        gains = []
        losses = []
        for i in range(1, len(ohlcv)):
          change = ohlcv[i][4] - ohlcv[i-1][4]  # 종가 기준
          if change >= 0:
            gains.append(change)
            losses.append(0)
          else:
            gains.append(0)
            losses.append(abs(change))
            
        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)
        
        if avg_loss == 0:
          rsi = 100
        else:
          rs = avg_gain / avg_loss
          rsi = 100 - (100 / (1 + rs))
        
        # 거래량 증감률 계산 (24시간 전 대비)
        volume_change = ((volume - float(ohlcv[-2][5])) / float(ohlcv[-2][5])) * 100 if float(ohlcv[-2][5]) > 0 else 0
        
        coin_data.append({
          'symbol': symbol,
          'price': last_price,
          'volume': volume,
          'change_24h': change_24h,
          'volume_change': volume_change,
          'rsi': rsi
        })
      
      # 매수 추천: RSI 낮고, 거래량 증가, 하락폭 큰 코인
      buy_signals = sorted(
        [coin for coin in coin_data if coin['rsi'] < 40 and coin['volume_change'] > 50],
        key=lambda x: (-x['volume_change'], x['change_24h'])
      )[:recommend_count]
      
      # 매도 추천: RSI 높고, 거래량 증가, 상승폭 큰 코인
      sell_signals = sorted(
        [coin for coin in coin_data if coin['rsi'] > 70 and coin['volume_change'] > 50],
        key=lambda x: (-x['change_24h'], -x['volume_change'])
      )[:recommend_count]
      
      return {
        'buy_signals': buy_signals,
        'sell_signals': sell_signals,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      }
      
    except Exception as e:
      print(f"매매 신호 분석 중 오류 발생: {str(e)}")
      return {}

  def print_trading_signals(self, recommend_count: int = 5):
    """
    매수/매도 추천 코인 출력
    """
    signals = self.get_trading_signals(recommend_count)
    if not signals:
      return
      
    print("\n=== 매매 추천 코인 ===")
    print(f"분석 시각: {signals['timestamp']}")
    
    print("\n[매수 추천]")
    for coin in signals['buy_signals']:
      print(f"{coin['symbol']}:")
      print(f"  현재가: {coin['price']:,.0f}원")
      print(f"  24시간 변동률: {coin['change_24h']:.2f}%")
      print(f"  거래량 변동률: {coin['volume_change']:.2f}%")
      print(f"  RSI: {coin['rsi']:.2f}")
    
    print("\n[매도 추천]")
    for coin in signals['sell_signals']:
      print(f"{coin['symbol']}:")
      print(f"  현재가: {coin['price']:,.0f}원")
      print(f"  24시간 변동률: {coin['change_24h']:.2f}%")
      print(f"  거래량 변동률: {coin['volume_change']:.2f}%")
      print(f"  RSI: {coin['rsi']:.2f}")


# 사용 예시
if __name__ == "__main__":
  market = UpbitMarket()
  
  # 시장 동향 요약
  market.print_market_summary()
  
  # 매매 추천 (상위 3개)
  market.print_trading_signals(3)
