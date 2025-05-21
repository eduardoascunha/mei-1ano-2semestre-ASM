import asyncio
from manager import Manager
from taxi import Taxi
from cliente import Client

async def main():
    manager = Manager("manager@localhost", "manager_password")
    await manager.start()

    taxi1 = Taxi("taxi1@localhost", "taxi_password", x=10, y=20)
    await taxi1.start()

    await asyncio.sleep(2)

    cliente1 = Client("cliente1@localhost", "client_password", x_pos=5, y_pos=5, x_dest=15, y_dest=25)
    await cliente1.start()

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())