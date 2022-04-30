import dosa


class Flush:
    def __init__(self, comms=None):
        if comms is None:
            comms = dosa.Comms()

        self.comms = comms

    def dispatch(self, target=None):
        trg = self.comms.build_payload(dosa.Messages.FLUSH)
        self.comms.send(trg, target)
        print("Flush request dispatched")
