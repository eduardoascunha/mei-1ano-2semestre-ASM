import spade
import jsonpickle
from spade.behaviour import CyclicBehaviour
from spade.message import Message

class Manager(spade.agent.Agent):
    async def setup(self):
        print("Manager Ativo.")
        self.lista_taxis = []
        self.lista_clientes = []

        self.add_behaviour(RegistarTaxiBehaviour())
        self.add_behaviour(ReceberPedidosBehaviour())

def dist(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

class RegistarTaxiBehaviour(CyclicBehaviour):
    async def run(self):
        resposta = await self.receive(timeout=10)  
        if resposta:
            if resposta.metadata.get("performative") == "REGISTER":
                
                taxi_data = jsonpickle.decode(resposta.body)
                print(f"[MANAGER] Taxi registado: {taxi_data['jid']}")

                self.agent.lista_taxis.append(taxi_data)

                msg = Message(to=resposta.sender)
                msg.set_metadata("performative", "CONFIRM")
                await self.send(msg)
            else:
                print("[MANAGER] Erro no registo do taxi: Metadata inválido")

class ReceberPedidosBehaviour(CyclicBehaviour):
    async def run(self):
        resposta = await self.receive(timeout=10)  
        if resposta:
            if resposta.metadata.get("performative") == "REQUEST":
                cliente_data = jsonpickle.decode(resposta.body)
                print(f"[MANAGER] Pedido de transporte recebido de {cliente_data['jid']}")

                self.agent.lista_clientes.append(cliente_data)

                msg = Message(to=resposta.sender)
                msg.set_metadata("performative", "CONFIRM")
                await self.send(msg)

                pos_min = float('inf')
                taxi_mais_perto = None

                for taxi in self.agent.lista_taxis:
                    if taxi["disponibilidade"]:
                        distancia = dist(cliente_data["x_pos"], cliente_data["y_pos"], taxi["x_loc"], taxi["y_loc"])
                        if distancia < pos_min:
                            pos_min = distancia
                            taxi_mais_perto = taxi

                if taxi_mais_perto:
                    print(f"[MANAGER] Táxi mais próximo: {taxi_mais_perto['jid']}")
                    msg = Message(to=taxi_mais_perto["jid"])
                    msg.set_metadata("performative", "REQUEST")
                    msg.body = jsonpickle.encode(cliente_data)
                    await self.send(msg)
                else:
                    print("[MANAGER] Nenhum táxi disponível.")
            else:
                print("[MANAGER] Erro no pedido de transporte: Metadata inválido")