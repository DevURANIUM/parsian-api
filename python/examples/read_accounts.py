import httpx
from parsianapi import Client

def main():
    with Client() as bank:
        print(bank.check_session())
        print(bank.accounts())
        print(bank.balance())

if __name__=='__main__':
    main()
