import pyupbit
from CheckBreakout import CheckBreakout
from CalculateAtr import CalculateAtr
from SendMessage import SendMessage

# Intervals = ["day","minute1","minute3","minute5","minute10","minute15","minute30","minute60","minute240","week","month"]
# Periods = [14, 21, 28, 35, 42, 49, 56]
################################################################################################################################################
KRW = 1000_000
Unit = 10000
Period = 14
nowInterval = "day"
fee = 0.0005
################################################################################################################################################
myCoins = set()
howManyCoin = {}
howManyPosition = {}
cutPriceATR = {}
nextBuyPrice = {}
################################################################################################################################################

while True:
    
    coins = pyupbit.get_tickers(fiat="KRW")

    for coin in coins:
        
        for i in range(150_0000):

            k = i

        df = pyupbit.get_ohlcv(coin, count=Period, interval=nowInterval)        
        
        if df is None:

            SendMessage(f"{coin} api 요청실패로 확인불가")
            continue        

        else :

            nowPrice = df.iloc[-1]['close']
        
            if coin[4:] in myCoins:

                if nowPrice <= cutPriceATR[coin] or CheckBreakout(df, Period/2, "low"):     

                    # upbit.sell_market_order(coin, myAsset[coin]['balance'])
                    if nowPrice <= cutPriceATR[coin]:
                        
                        cause = "cutPriceATR"
                    
                    else:
                    
                        cause = "Breakout"

                    Sell = nowPrice * howManyCoin[coin] * (1-fee)
                    KRW += Sell
                    SendMessage(f"{coin} {cause}에 의해 매도, 결과 {Sell - howManyPosition[coin] * Unit}, {KRW}")

                    del howManyCoin[coin]
                    del howManyPosition[coin]
                    del cutPriceATR[coin]
                    del nextBuyPrice[coin]
                    myCoins.remove(coin)
                
                else:

                    if nowPrice >= nextBuyPrice[coin]:

                        if KRW < Unit*1.0005 or howManyPosition[coin]>=15:

                            if KRW < Unit*1.0005:
                                
                                cause = "보유 현금 부족"
                            
                            else:
                            
                                cause = "Breakout"

                            SendMessage(f"{coin} {cause}으로 추가매수 실패, {KRW}")
                            continue
                    
                        # upbit.buy_market_order(coin, Unit)
                        Buy = Unit * (1+fee)
                        KRW -= Buy
                        SendMessage(f"{coin} {nowPrice} 추가매수, {KRW}")

                        howManyCoin[coin] += Unit/nowPrice
                        howManyPosition[coin] += 1
                        df = CalculateAtr(df, Period)
                        ATR = df.iloc[-1]['ATR']
                        cutPriceATR[coin] = nowPrice - 2*ATR
                        nextBuyPrice[coin] = nowPrice + ATR
                    
            else:

                if CheckBreakout(df, Period, "high") == True:

                    if KRW < Unit * (1 + fee) :
                        
                        SendMessage(f"{coin} 보유 현금 부족으로 매수 실패, {KRW}")

                    else:

                        # upbit.buy_market_order(coin, Unit)
                        Buy = Unit * (1+fee)
                        KRW -= Buy
                        SendMessage(f"{coin} {nowPrice} 매수 진입, {KRW}")

                        howManyCoin[coin] = Unit/nowPrice
                        howManyPosition[coin] = 1
                        df = CalculateAtr(df, Period)
                        ATR = df.iloc[-1]['ATR']
                        cutPriceATR[coin] = nowPrice - 2*ATR
                        nextBuyPrice[coin] = nowPrice + ATR
                        myCoins.add(coin[4:])