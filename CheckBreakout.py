def CheckBreakout(data, period=20, hl="high"):
    """
    돌파를 체크하는 함수
    
    매개변수:
    data (pd.DataFrame): 'high', 'low', 'close' 열이 포함된 pandas DataFrame
    period (int): 기준 기간. 기본값은 20일
    hl (string): 돌파 대상. 기본값은 신고가
    
    반환값:
    breakout (boolean): 현재가와 기준가의 비교 결과
    """

    period = int(period)

    # 현재가
    last_close = data.iloc[-1]['close']

    # 기준가
    if hl == "high":
        hlPrice = data.iloc[-(period+1):-1]['high'].max()
        breakout = last_close >= hlPrice
    elif hl == "low":
        hlPrice = data.iloc[-(period+1):-1]['low'].min()
        breakout = last_close <= hlPrice
    else:
        raise ValueError("Invalid value for 'hl'. Use 'high' or 'low'.")

    return breakout
