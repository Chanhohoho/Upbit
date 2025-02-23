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
