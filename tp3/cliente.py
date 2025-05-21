import spade
import jsonpickle
from spade.behaviour import OneShotBehaviour
from spade.message import Message

class Client(spade.agent.Agent):
    def __init__(self, jid, password, x_pos, y_pos, x_dest, y_dest):
        super().__init__(jid, password)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_dest = x_dest
        self.y_dest = y_dest

    async def setup(self):
        print(f"Cliente {self.jid} Ativo.")
        self.manager_jid = "manager@localhost"

        self.add_behaviour(PedirTransporteBehaviour())

class PedirTransporteBehaviour(OneShotBehaviour):
    async def run(self):
        cliente_data = {
            "jid": self.agent.jid,
            "x_pos": self.agent.x_pos,
            "y_pos": self.agent.y_pos,
            "x_dest": self.agent.x_dest,
            "y_dest": self.agent.y_dest
        }

        msg = Message(to=self.agent.manager_jid)
        msg.set_metadata("performative", "REQUEST")  
        msg.body = jsonpickle.encode(cliente_data)

        await self.send(msg)
        print(f"[CLIENTE] Pedido de transporte enviado para {self.agent.manager_jid}")

        resposta = await self.receive(timeout=10)
        if resposta and resposta.metadata.get("performative") == "CONFIRM":
            print(f"[CLIENTE] Pedido confirmado!")
        else:
            print("[CLIENTE] Erro no pedido.")