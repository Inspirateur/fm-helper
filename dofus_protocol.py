import scapy.all as scapy


PORT = 5555


def print_bin(load):
	print(", ".join(f"{b:08b}" for b in load))


class DofusListener:
	def __init__(self, callback):
		self.callback = callback
		print("listening to dofus packet ...")
		scapy.sniff(prn=self.handle, filter=f"tcp src port {PORT}")

	def handle(self, pkt: scapy.Packet):
		# if there's data in the packet
		if scapy.Raw in pkt:
			load = pkt[scapy.Raw].load
			# normal parsing of the packet
			while len(load):
				head = int.from_bytes(load[0:2], byteorder="big")
				msg_id = head >> 2
				lentype = head & 3
				lenmsg = int.from_bytes(load[2:2+lentype], byteorder="big")
				lenload = len(load) - (2+lentype)
				if lenmsg > lenload:
					break
				self.callback(DofusPacket(msg_id, load[2 + lentype:2 + lentype + lenmsg]))
				load = load[2 + lentype + lenmsg:]


class DofusPacket:
	ID_FM_ITEM = 819
	ID_START_FM = 7187
	ID_ADD = 88
	ID_REMOVED = 1377

	def __init__(self, pck_id, msg):
		self.id = pck_id
		self.msg = msg

	def __str__(self):
		return f"{self.id}: ({len(list(self.msg))}) {list(self.msg)}"

	def __getitem__(self, item):
		if isinstance(item, int):
			if item < 0:
				item = len(self.msg)+item
			item = slice(item, item+1)
		return int.from_bytes(self.msg[item], byteorder="big")
