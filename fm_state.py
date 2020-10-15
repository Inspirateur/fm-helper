from collections import defaultdict
import csv
import dofus_protocol as dp


class Item:
	def __init__(self, item_id, stats):
		self.id = item_id
		self._stats = stats

	@staticmethod
	def from_packet(pkt: dp.DofusPacket, offset):
		# skip the first or second byte
		i = offset
		if pkt[i] >= 128:
			i += 1
		i += 2
		# read the amount of stats
		count = pkt[i]
		i += 1

		def read_value():
			nonlocal i
			value = pkt[i]
			if value >= 128:
				value += pkt[i+1]*64
				i += 1
			return value

		stats = defaultdict(int)
		while count:
			# skip 1 octet (i still don't know what 26 is for)
			i += 1
			# read whether or not the stat is a unique value
			unique = pkt[i] == 64
			i += 1
			# read the id, for some reason it's on 2 bytes if the first byte is > 128
			stat_id = read_value()
			i += 1
			# read the value
			if unique:
				stats[stat_id] = read_value()
				i += 1
			else:
				min_val = read_value()
				i += 1
				max_val = read_value()
				i += 1
				stats[stat_id] = (min_val, max_val)
			count -= 1
		# read the item unique id
		item_id = pkt[i:i+2]
		return Item(item_id, stats)

	def __getitem__(self, item):
		return self._stats[item]

	def __setitem__(self, key, value):
		self._stats[key] = value

	def __len__(self):
		return len(self._stats)

	def __str__(self):
		return f"{self.id} {dict(self._stats)}"

	def keys(self):
		return self._stats.keys()


class FMState:
	def __init__(self):
		self.history = []
		self.slots = {}
		self.last_remove = None
		self.pools = defaultdict(float)
		# read the stats.csv here
		self.item_info = {}
		with open("stats.csv", "r") as fstats:
			stats = csv.reader(fstats)
			for row in list(stats)[1:]:
				self.item_info[int(row[0])] = {"name": row[1], "poids": float(row[2])}

	def update(self, pkt: dp.DofusPacket):
		if pkt.id == dp.DofusPacket.ID_START_FM:
			print("opened craft window")
		elif pkt.id == dp.DofusPacket.ID_ADD:
			item = Item.from_packet(pkt, 4)
			self.slots[item.id] = item
			print(f"added an item/rune {item}")
			# print(pkt)
		elif pkt.id == dp.DofusPacket.ID_REMOVED:
			item_id = pkt[1:3]
			if item_id in self.slots:
				self.last_remove = self.slots[item_id]
			self.slots.pop(item_id, None)
			print(f"removed item/rune {item_id}")
			# print(pkt)
		elif pkt.id == dp.DofusPacket.ID_FM_ITEM:
			# retrieve the item
			new_item = Item.from_packet(pkt, 2)
			# retrieve the old item
			old_item = self.slots[new_item.id]
			self.slots[new_item.id] = new_item
			# retrieve the rune
			keys = list(self.slots.keys())
			keys.remove(new_item.id)
			if keys:
				rune = self.slots[keys[0]]
			else:
				rune = self.last_remove
			# compute the delta stats
			delta_stats = {}
			poids = {}
			for stat in set(new_item.keys()) | set(old_item.keys()):
				if stat in self.item_info:
					statname = self.item_info[stat]["name"]
					new_stat = new_item[stat] - old_item[stat]
					if new_stat:
						delta_stats[statname] = new_stat
						poids[statname] = self.item_info[stat]["poids"]

			# update the pool
			if pkt[-1] != 1:
				# the pool changed

				# we compute the gain or loss incurred by stat changes
				self.pools[new_item["id"]] -= sum(delta*poids[stat] for stat, delta in delta_stats.items())
				# clamp the pool to 0 again
				if self.pools[new_item["id"]] < 0:
					self.pools[new_item["id"]] = 0

				if pkt[0] != 2:
					# it was a failure, we pay the rune cost if enough pool is left
					rune_id = list(rune.keys())[0]
					rune_cost = rune[rune_id]*self.item_info[rune_id]["poids"]
					if self.pools[new_item["id"]] >= rune_cost:
						self.pools[new_item["id"]] -= rune_cost

			print(f"FM'ed item - new pool {self.pools[new_item['id']]:.2f} - delta {dict(delta_stats)} ")
