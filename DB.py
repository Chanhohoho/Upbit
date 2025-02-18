import sqlite3

# DB 연결
conn = sqlite3.connect('Coin.db')
cursor = conn.cursor()

# 테이블 생성 (설정값 저장용)
cursor.execute('''
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value REAL
)
''')

# 테이블 생성 (코인 상태 저장용)
cursor.execute('''
CREATE TABLE IF NOT EXISTS coin_state (
    coin TEXT PRIMARY KEY,
    cutPriceATR REAL,
    nextBuyPrice REAL,
    howManyPosition INTEGER
)
''')

# DB 커밋 및 연결 종료
# conn.commit()
# conn.close()

def load_settings():
    conn = sqlite3.connect('Coin.db')
    cursor = conn.cursor()

    # 설정값 불러오기
    cursor.execute('SELECT key, value FROM settings')
    settings = cursor.fetchall()

    settings_dict = {key: value for key, value in settings}
    conn.close()
    return settings_dict

# 사용 예시
# settings = load_settings()

# UNIT = int(settings.get('UNIT', 10000))
# FEE = float(settings.get('FEE', 0.0005))

def update_setting(key, value):
    conn = sqlite3.connect('Coin.db')
    cursor = conn.cursor()

    # 설정값 갱신
    cursor.execute('''
    INSERT INTO settings (key, value)
    VALUES (?, ?)
    ON CONFLICT(key) DO UPDATE SET value = ?
    ''', (key, value, value))

    conn.commit()
    conn.close()

# 사용 예시
# update_setting('UNIT', 15000)  # UNIT 값을 15000으로 갱신

def load_coin_state(coin):
    conn = sqlite3.connect('Coin.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM coin_state WHERE coin = ?', (coin,))
    coin_state = cursor.fetchone()

    conn.close()
    if coin_state:
        return {
            'coin': coin_state[0],
            'cutPriceATR': coin_state[1],
            'nextBuyPrice': coin_state[2],
            'howManyPosition': coin_state[3]
        }
    return None

def update_coin_state(coin, cutPriceATR, nextBuyPrice, howManyPosition):
    conn = sqlite3.connect('Coin.db')
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO coin_state (coin, cutPriceATR, nextBuyPrice, howManyPosition)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(coin) DO UPDATE SET
        cutPriceATR = ?, nextBuyPrice = ?, howManyPosition = ?
    ''', (coin, cutPriceATR, nextBuyPrice, howManyPosition,
          cutPriceATR, nextBuyPrice, howManyPosition))

    conn.commit()
    conn.close()

# 사용 예시
# coin_state = load_coin_state('KRW-BTC')  # 'KRW-BTC' 코인의 상태 불러오기
# update_coin_state('KRW-BTC', 50000, 51000, 1, 0.5, 60, 30, 100000)  # 'KRW-BTC' 코인의 상태 갱신

def delete_coin_state(coin):
    """손절한 코인을 DB에서 삭제"""
    conn = sqlite3.connect('Coin.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM coin_state WHERE coin = ?', (coin,))
    
    conn.commit()
    conn.close()

# 사용 예시
# delete_coin_state('KRW-BTC')  # 'KRW-BTC' 코인을 DB에서 삭제
