import spade
import asyncio
import random

class AguardaCompradorBehaviour(spade.behaviour.CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)  
        if msg:
            print(f"[Seller] Mensagem recebida de {msg.sender}: deseja comprar {msg.body}")

            if msg.body in self.agent.lista_de_itens:
                resp = spade.message.Message(to=str(msg.sender))
                resp.set_metadata("performative", "CONFIRM")
                resp.body = f"Confirmado: {msg.body} por {self.agent.lista_de_itens[msg.body]} créditos."
                await self.send(resp)

                self.agent.lucro_total += self.agent.lista_de_itens[msg.body]
                print(f"[Seller] Venda confirmada de {msg.body} por {self.agent.lista_de_itens[msg.body]} créditos.")
            else:
                resp = spade.message.Message(to=str(msg.sender))
                resp.set_metadata("performative", "REFUSE")
                resp.body = f"Produto {msg.body} não disponível."
                await self.send(resp)
                print(f"[Seller] Pedido recusado. Produto {msg.body} não disponível.")
        else:
            print("[Seller] Nenhuma mensagem recebida.")

class ImprimeLucroBehaviour(spade.behaviour.PeriodicBehaviour):
    async def run(self):
        print(f"[Seller] Lucro total até agora: {self.agent.lucro_total} créditos.")

class SellerAgent(spade.agent.Agent):
    async def setup(self):
        print("[Seller] Agente Seller Ativo.")
        self.lista_de_itens = {'Apple': 5, 'Banana': 3, 'Grapefruit': 10, 'Orange': 7}
        self.lucro_total = 0

        venda = AguardaCompradorBehaviour()
        self.add_behaviour(venda)

        lucro = ImprimeLucroBehaviour(period=3)
        self.add_behaviour(lucro)

class CompraBehaviour(spade.behaviour.OneShotBehaviour):
    async def run(self):
        lista_de_itens = ['Apple', 'Banana', 'Grapefruit', 'Orange', 'Pear', 'Melon', 'Strawberry']
        produto_escolhido = random.choice(lista_de_itens)  
        vendedor_jid = "vendedor@localhost"

        msg = spade.message.Message(to=vendedor_jid)
        msg.set_metadata("performative", "REQUEST")
        msg.body = produto_escolhido
        await self.send(msg)
        print(f"[Buyer] Pedido de compra enviado para {vendedor_jid}: {produto_escolhido}")

        resposta = await self.receive(timeout=5)
        if resposta:
            print(f"[Buyer] Resposta do vendedor: {resposta.body}")
        else:
            print("[Buyer] Não recebeu resposta do vendedor.")

class BuyerAgent(spade.agent.Agent):
    async def setup(self):
        print("[Buyer] Agente Buyer Ativo.")
        comportamento = CompraBehaviour()
        self.add_behaviour(comportamento)

async def main():
    vendedor = SellerAgent("vendedor@localhost", "NOPASSWORD")
    await vendedor.start()
    await asyncio.sleep(1)
    
    buyer1 = BuyerAgent("buyer1@localhost", "NOPASSWORD")
    await buyer1.start()
    await asyncio.sleep(6)
    
    buyer2 = BuyerAgent("buyer2@localhost", "NOPASSWORD")
    await buyer2.start()
    await asyncio.sleep(3) 
    
    await buyer1.stop()
    await buyer2.stop()
    await vendedor.stop()

if __name__ == "__main__":
    asyncio.run(main())
