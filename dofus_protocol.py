import scapy.all as scapy


PORT = 5555


def print_bin(load):
	print(", ".join(f"{b:08b}" for b in load))


class DofusListener:
	def __init__(self, callback):
		self._buffer = []
		self._id = None
		self._len = None
		self.callback = callback
		print("listening to dofus packet ...")
		scapy.sniff(prn=self.handle, filter=f"src port {PORT}")

	def handle(self, pkt: scapy.Packet):
		# if there's data in the packet
		if scapy.Raw in pkt:
			load = pkt[scapy.Raw].load
			# completing a message from an earlier packet
			if self._buffer:
				if self._len <= len(load):
					self._buffer.append(load[:self._len])
					self.callback(DofusPacket(self._id, b"".join(self._buffer)))
					self._buffer.clear()
					load = load[self._len:]
				else:
					self._buffer.append(load)
					self._len -= len(load)
					return
			# normal parsing of the packet
			while len(load):
				head = int.from_bytes(load[0:2], byteorder="big")
				msg_id = head >> 2
				lentype = head & 3
				lenmsg = int.from_bytes(load[2:2+lentype], byteorder="big")
				lenload = len(load) - (2+lentype)
				if lenmsg <= lenload:
					self.callback(DofusPacket(msg_id, load[2+lentype:2+lentype+lenmsg]))
					load = load[2+lentype+lenmsg:]
				else:
					self._id = msg_id
					self._len = lenmsg-lenload
					self._buffer.append(load[2+lentype:])
					break
			# basic error management
			if self._len and self._len > 10**3:
				print("Read a non-sensical message length, probably missed the real header, resetting.")
				self._buffer.clear()


class DofusPacket:
	ID_FM_ITEM = 8399
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
			item = slice(item, item+1)
		return int.from_bytes(self.msg[item], byteorder="big")
