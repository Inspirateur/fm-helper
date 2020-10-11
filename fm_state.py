import dofus_protocol as dp


class FMState:
	def __init__(self):
		self.history = []
		self.item = None
		self.rune = None

	def update(self, pkt: dp.DofusPacket):
		if pkt.id == dp.DofusPacket.ADD_ITEM:
			print("edited item/rune")
			print(pkt)
		elif pkt.id == dp.DofusPacket.FM:
			print("FM")
			print(pkt)
