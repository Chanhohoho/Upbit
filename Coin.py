from Calculate import Calculate, CheckBreakout
from SendMessage import SendMessage
from DB import load_settings, update_coin_state, delete_coin_state, load_coin_state  # DB 연동
from _Key.Key import upbit
import pyupbit
import gc
import time

# 기본 설정값
# UNIT = 10000  # 기본 매수 단위
# FEE = 0.0005  # 거래 수수료
# PERIOD = 56  # 장기 돌파 체크 기간
# PERIOD_SHORT = 7 # 단기 돌파 체크 기간
# GOAL = 10  # 최대 보유 포지션
# UNDER = 2.5  # 손절 ATR 배수
# CUTPERCENT = 4 # 손절 %
# VOLUME = 3  # 진입 거래량 배수

# ADX_FILTER = 20 # 추세 이탈 필터
# ADX_THRESHOLD = 25  # 강한 추세 필터
# RSI_BUY = 55  # 상승 추세 진입 기준
# RSI_SELL = 45  # 하락 추세 진입 기준

# 상태 저장
Watchlist = set()
cutPriceATR = {}
nextBuyPrice = {}
howManyPosition = {}

coins = pyupbit.get_tickers(fiat="KRW")
for coin in coins:
    state = load_coin_state(coin)
    if state:
        Watchlist.add(coin)
        cutPriceATR[coin] = state['cutPriceATR']
        nextBuyPrice[coin] = state['nextBuyPrice']
        howManyPosition[coin] = state['howManyPosition']

while True:
    gc.collect()  # 메모리 정리

    settings = load_settings()
    UNIT = int(settings.get('UNIT', 10000))
    FEE = float(settings.get('FEE', 0.0005))
    PERIOD = int(settings.get('PERIOD', 56))
    PERIOD_SHORT = int(settings.get('PERIOD_SHORT', 5))
    GOAL = int(settings.get('GOAL', 10))
    UNDER = float(settings.get('UNDER', 2.5))
    CUTPERCENT = float(settings.get('CUTPERCENT', 4))
    VOLUME = float(settings.get('VOLUME', 3))

    ADX_FILTER = float(settings.get('ADX_FILTER', 20))
    ADX_THRESHOLD = float(settings.get('ADX_THRESHOLD', 25))
    RSI_BUY = float(settings.get('RSI_BUY', 55))
    RSI_SELL = float(settings.get('RSI_SELL', 45))

    try:
        coins = pyupbit.get_tickers(fiat="KRW")
        time.sleep(1)  # API 과부하 방지
    
    except:
        SendMessage(f"현재 원화로 거래중인 API 요청 실패로 확인 불가")
        time.sleep(1)  # API 과부하 방지
        continue
    
    for coin in coins:
        try:
            df = pyupbit.get_ohlcv(coin, count=PERIOD, interval="day")
            nowPrice = df.iloc[-1]['close']
            df = Calculate(df)
            ATR = df.iloc[-1]['ATR']
            RSI = df.iloc[-1]['RSI']
            ADX = df.iloc[-1]['ADX']
            UP = ATR
            DOWN = UNDER * ATR

            ATR_Percent = df.iloc[-1]['ATR_Percent']
            if ATR_Percent > CUTPERCENT:
                UP = CUTPERCENT * (nowPrice // 100)
                DOWN = UNDER * CUTPERCENT * (nowPrice // 100)

        except:
            SendMessage(f"{coin} API 요청 실패로 확인 불가")
            time.sleep(1)  # API 과부하 방지
            continue
        
        if coin in Watchlist:
            # ✅ 추가 매수 (강한 상승이 나오면 추가 매수)
            if nowPrice >= nextBuyPrice[coin] and howManyPosition[coin] < GOAL:
                try:
                    KRW = upbit.get_balance('KRW')
                    time.sleep(1)  # API 과부하 방지

                except:
                    SendMessage(f"현금 보유량 조회 API 요청 실패로 확인 불가")
                    time.sleep(1)  # API 과부하 방지
                    continue

                if KRW >= UNIT * (1 + FEE):
                    try:
                        upbit.buy_market_order(coin, UNIT)
                        time.sleep(1)  # API 과부하 방지
                    
                    except:
                        SendMessage(f"{coin} 매수 API 요청 실패로 확인 불가")
                        time.sleep(1)  # API 과부하 방지
                        continue

                    howManyPosition[coin] += 1
                    cutPriceATR[coin] = nowPrice - DOWN
                    nextBuyPrice[coin] = nowPrice + UP

                    update_coin_state(coin, cutPriceATR[coin], nextBuyPrice[coin], howManyPosition[coin])
                    
                else:
                    SendMessage(f"{coin} 현금 부족으로 매수 실패")
                    time.sleep(1)  # API 과부하 방지

            # ✅ 손절 조건 (추세가 무너지는 경우)
            elif (ADX < ADX_FILTER or RSI < RSI_SELL) or CheckBreakout(df, PERIOD // 4, "low") or nowPrice < cutPriceATR[coin]:
                if howManyPosition[coin] != 0:
                    try:
                        upbit.sell_market_order(coin, upbit.get_balance(coin))
                        time.sleep(1)  # API 과부하 방지
                    
                    except:
                        SendMessage(f"{coin} 매도 API 요청 실패로 확인 불가")
                        time.sleep(1)  # API 과부하 방지
                        continue

                Watchlist.remove(coin)
                cutPriceATR.pop(coin, None)
                nextBuyPrice.pop(coin, None)
                howManyPosition.pop(coin, None)

                delete_coin_state(coin)
            
        else:
            # ✅ 추세 강한 종목만 진입 (ADX > 25 & RSI > 55)
            if ADX < ADX_THRESHOLD or RSI < RSI_BUY:
                continue
            
            # ✅ 진입 조건 (단기 고점 돌파(== 눌림목) & 거래량 증가)
            if (CheckBreakout(df, PERIOD_SHORT, 'high') and df['volume'].iloc[-1] > df['volume'].rolling(PERIOD_SHORT).mean().iloc[-1] * VOLUME) or (CheckBreakout(df, PERIOD, 'high')):
                Watchlist.add(coin)
                cutPriceATR[coin] = nowPrice - DOWN
                nextBuyPrice[coin] = nowPrice + UP
                howManyPosition[coin] = 0

                update_coin_state(coin, cutPriceATR[coin], nextBuyPrice[coin], howManyPosition[coin])
            
        time.sleep(0.05)  # API 과부하 방지
