import scapy.all as scapy


PORT = 5555


class DofusListener:
	def __init__(self, callback):
		self.callback = callback
		scapy.sniff(prn=self.handle, filter=f"dst port {PORT}")

	def handle(self, pkt):
		if scapy.Raw in pkt:
			load = pkt[scapy.Raw].load
			head = int.from_bytes(load[0:2], byteorder="big")
			msg_id = head >> 2
			lentype = head & 3
			lenmsg = int.from_bytes(load[6:6+lentype], byteorder="big")
			assert lenmsg <= len(load)-(6+lentype)
			msg = load[6+lentype:6+lentype+lenmsg]
			print(", ".join(f"{b:08b}" for b in load))
			self.callback(DofusPacket(msg_id, msg))


class DofusPacket:
	ADD_ITEM = 3601
	FM = 4086

	def __init__(self, pck_id, msg):
		self.id = pck_id
		self.msg = msg

	def __str__(self):
		return f"{self.id}: ({len(list(self.msg))}) {list(self.msg)}"
