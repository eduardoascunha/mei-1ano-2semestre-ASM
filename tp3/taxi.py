import spade
import jsonpickle
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
import asyncio

class Taxi(spade.agent.Agent):
    def __init__(self, jid, password, x, y):
        super().__init__(jid, password)
        self.x_loc = x
        self.y_loc = y
        self.disponibilidade = True

    async def setup(self):
        print(f"Taxi {self.jid} Ativo.")
        self.manager_jid = "manager@localhost"

        self.add_behaviour(RegistarBehaviour())
        self.add_behaviour(TrataPedidosBehaviour())

    def set_disponibilidade(self, disp):
        self.disponibilidade = disp

class RegistarBehaviour(OneShotBehaviour):
    async def run(self):
        msg = Message(to=self.agent.manager_jid)
        msg.set_metadata("performative", "REGISTER")  

        taxi_data = {
            "jid": self.agent.jid,
            "x_loc": self.agent.x_loc,
            "y_loc": self.agent.y_loc,
            "disponibilidade": self.agent.disponibilidade
        }
        msg.body = jsonpickle.encode(taxi_data)

        await self.send(msg)
        print(f"[TAXI] Pedido de registo enviado para {self.agent.manager_jid}")

        resposta = await self.receive(timeout=10)
        if resposta and resposta.metadata.get("performative") == "CONFIRM":
            print(f"[TAXI] Taxi registado!")
        else:
            print("[TAXI] Erro no registo.")

class TrataPedidosBehaviour(CyclicBehaviour):
    async def run(self):
        resposta = await self.receive(timeout=10)  
        if resposta:
            if resposta.metadata.get("performative") == "REQUEST":
                self.agent.set_disponibilidade(False)
                cliente_info = jsonpickle.decode(resposta.body)
                print(f"[TAXI] A ir para ({cliente_info['x_dest']},{cliente_info['y_dest']})!")

                # simula a viagem
                await asyncio.sleep(5)

                print(f"[TAXI] Chegamos a ({cliente_info['x_dest']},{cliente_info['y_dest']})!")
                self.agent.x_loc = cliente_info["x_dest"]
                self.agent.y_loc = cliente_info["y_dest"]

                msg = Message(to=self.agent.manager_jid)
                msg.set_metadata("performative", "FINALIZE")
                msg.body = jsonpickle.encode(self.agent)
                await self.send(msg)
                print(f"[TAXI] Final de viagem enviado.")

                self.agent.set_disponibilidade(True)