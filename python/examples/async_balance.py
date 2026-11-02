import asyncio
from parsianapi import AsyncClient

async def main():
    async with AsyncClient() as bank:
        print(await bank.check_session())
        print(await bank.balance())

if __name__=='__main__':
    asyncio.run(main())
