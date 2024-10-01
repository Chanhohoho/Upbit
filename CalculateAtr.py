import pandas as pd
import numpy as np

def CalculateAtr(data, period=20):
    """
    ATR(Average True Range)를 계산하는 함수
    
    매개변수:
    data (pd.DataFrame): 'high', 'low', 'close' 열이 포함된 pandas DataFrame
    period (int): ATR을 계산할 기간. 기본값은 20일
    
    반환값:
    pd.Series: ATR 값이 저장된 pandas Series
    """
    
    # TR(True Range) 계산
    high_low = data['high'] - data['low']
    high_close = np.abs(data['high'] - data['close'].shift())
    low_close = np.abs(data['low'] - data['close'].shift())
    
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # ATR 계산 (기본적으로 20일간의 TR의 이동평균)
    atr = tr.rolling(window=period, min_periods=1).mean()
    
    # ATR이 종가 대비 몇 퍼센트 변동인지 계산    
    atr_percent = (atr / data['close']) * 100
    
    # ATR과 ATR 퍼센트 변동을 데이터프레임에 추가
    data['ATR'] = atr
    data['ATR_Percent'] = atr_percent
    
    return data