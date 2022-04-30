import dosa


class Trigger:
    def __init__(self, comms=None):
        if comms is None:
            comms = dosa.Comms()

        self.comms = comms

    def fire(self, target=None):
        aux = bytearray(b'\x02')
        for i in range(64):
            aux += b'\x00'

        self.comms.send(self.comms.build_payload(dosa.Messages.TRIGGER, aux), target)
        print("Trigger dispatched")
