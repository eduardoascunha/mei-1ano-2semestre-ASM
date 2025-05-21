import spade
import asyncio

class receiverBehaviour(spade.behaviour.CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)  # Aguarda mensagem por até 10 segundos
        if msg:
            print(f"[Receiver] Mensagem recebida de {msg.sender}: {msg.body}")
        else:
            print("[Receiver] Nenhuma mensagem recebida.")

class receiver_agent(spade.agent.Agent):
    async def setup(self):
        print("Agente pronto para receber mensagens.")
        comportamento = receiverBehaviour()
        self.add_behaviour(comportamento)  
    
class senderBehaviour(spade.behaviour.OneShotBehaviour):
    async def run(self):
        receiver_jid = "receiver@localhost"  
        msg = spade.message.Message(to=receiver_jid)
        msg.body = "Hello World!"
        
        await self.send(msg)
        print("Mensagem enviada ao receiver.")

class sender_agent(spade.agent.Agent):
    async def setup(self):
        print("Agente vai enviar...")  
        comportamento = senderBehaviour()
        self.add_behaviour(comportamento)

async def main():
    receiver = receiver_agent("receiver@localhost", "NOPASSWORD")
    await receiver.start()

    await asyncio.sleep(1)
    sender1 = sender_agent("sender1@localhost", "NOPASSWORD")
    await sender1.start()

    await asyncio.sleep(2)
    sender2 = sender_agent("sender2@localhost", "NOPASSWORD")
    await sender2.start()

    await asyncio.sleep(1)
    await sender1.stop()
    await sender2.stop()
    await receiver.stop()

if __name__ ==  "__main__":
    spade.run(main())