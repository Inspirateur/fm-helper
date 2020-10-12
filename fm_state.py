import dofus_protocol as dp


class FMState:
	def __init__(self):
		self.history = []
		self.item = None
		self.rune = None

	def update(self, pkt: dp.DofusPacket):
		if pkt.id == dp.DofusPacket.ID_START_FM:
			print("opened craft window")
		elif pkt.id == dp.DofusPacket.ID_ADD:
			print("added an item/rune")
			print(pkt)
		elif pkt.id == dp.DofusPacket.ID_REMOVED:
			print("removed an item/rune")
			print(pkt)
		elif pkt.id == dp.DofusPacket.ID_FM_ITEM:
			print("FM'ed am item")
			print(pkt)
