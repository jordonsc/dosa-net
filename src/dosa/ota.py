import dosa


class Ota:
    def __init__(self, comms=None):
        if comms is None:
            comms = dosa.Comms()

        self.comms = comms

    def dispatch(self, target=None):
        trg = self.comms.build_payload(dosa.Messages.OTA)
        self.comms.send(trg, target)
        print("OTA update requested")
