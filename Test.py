from _Key.Key import upbit
from pprint import pprint
from SendMessage import SendMessage

# pprint(upbit.get_balances())

KRW = upbit.get_balance('KRW')

# try:
#     upbit.get_balance('KRW')
# except:
#     print("HI")

print(KRW)
SendMessage(f"{123}")
# print(type(KRW))

# git reset --hard HEAD  # 로컬 변경 사항 모두 취소
# git pull  # 다시 pull 실행
