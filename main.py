import dofus_protocol as dp
from fm_state import FMState


def packet_handle(pkt: dp.DofusPacket):
	state.update(pkt)


state = FMState()
listener = dp.DofusListener(packet_handle)
