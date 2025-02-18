import pandas as pd
import numpy as np

def CheckBreakout(data: pd.DataFrame, period: int = 14, breakout_type: str = "high") -> bool:
    """
    특정 기간의 고점 또는 저점을 돌파했는지 확인하는 함수.
    
    Args:
        data (pd.DataFrame): 'high', 'low', 'close' 열이 포함된 데이터프레임
        period (int, optional): 돌파 기준 기간 (기본값: 14일)
        breakout_type (str, optional): "high"는 신고가 돌파, "low"는 신저가 돌파 (기본값: "high")
    
    Returns:
        bool: 돌파 여부 (True: 돌파, False: 미돌파)
    """

    last_close = data.iloc[-1]['close']
    
    if breakout_type == "high":
        threshold_price = data.iloc[-(period+1):-1]['high'].max()
        return last_close >= threshold_price
    else:
        threshold_price = data.iloc[-(period+1):-1]['low'].min()
        return last_close <= threshold_price

def CalculateATR(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    ATR(Average True Range) 및 ATR 퍼센트를 계산하는 함수.
    
    Args:
        data (pd.DataFrame): 'high', 'low', 'close' 열이 포함된 데이터프레임
        period (int, optional): ATR을 계산할 기간 (기본값: 14일)
    
    Returns:
        pd.DataFrame: ATR과 ATR_Percent가 추가된 데이터프레임
    """
    high_low = data['high'] - data['low']
    high_close = np.abs(data['high'] - data['close'].shift(1))
    low_close = np.abs(data['low'] - data['close'].shift(1))
    
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period, min_periods=1).mean()
    
    data['ATR'] = atr
    data['ATR_Percent'] = (atr / data['close']) * 100
    
    return data

def CalculateRSI(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    RSI(Relative Strength Index)를 계산하는 함수.
    
    Args:
        data (pd.DataFrame): 'close' 열이 포함된 데이터프레임
        period (int, optional): RSI를 계산할 기간 (기본값: 14일)
    
    Returns:
        pd.DataFrame: RSI 값이 추가된 데이터프레임
    """
    delta = data['close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(window=period, min_periods=1).mean()
    avg_loss = pd.Series(loss).rolling(window=period, min_periods=1).mean()

    rs = avg_gain / (avg_loss + 1e-10)  # Zero division 방지
    data['RSI'] = 100 - (100 / (1 + rs))
    
    return data

def CalculateADX(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    ADX(Average Directional Index)를 계산하는 함수.
    
    Args:
        data (pd.DataFrame): 'high', 'low', 'close' 열이 포함된 데이터프레임
        period (int, optional): ADX를 계산할 기간 (기본값: 14일)
    
    Returns:
        pd.DataFrame: ADX, +DI, -DI 값이 추가된 데이터프레임
    """
    high, low = data['high'], data['low']
    
    plus_dm = np.where(high.diff() > low.diff(), high.diff(), 0)
    minus_dm = np.where(low.diff() > high.diff(), low.diff(), 0)

    atr = (high - low).rolling(window=period).mean()

    plus_di = (100 * (pd.Series(plus_dm).rolling(window=period).mean() / atr)).fillna(0)
    minus_di = (100 * (pd.Series(minus_dm).rolling(window=period).mean() / atr)).fillna(0)

    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(window=period).mean()

    data['+DI'] = plus_di
    data['-DI'] = minus_di
    data['ADX'] = adx

    return data

def Calculate(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    ATR, RSI, ADX를 한 번에 계산하는 함수.
    
    Args:
        data (pd.DataFrame): 'high', 'low', 'close' 열이 포함된 데이터프레임
        atr_period (int, optional): ATR을 계산할 기간 (기본값: 20일)
        rsi_period (int, optional): RSI를 계산할 기간 (기본값: 14일)
        adx_period (int, optional): ADX를 계산할 기간 (기본값: 14일)
    
    Returns:
        pd.DataFrame: ATR, ATR_Percent, RSI, ADX, +DI, -DI가 추가된 데이터프레임
    """
    data = CalculateATR(data, period=period)
    data = CalculateRSI(data, period=period)
    data = CalculateADX(data, period=period)

    return data
