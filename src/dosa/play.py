import dosa


class Play:
    def __init__(self, comms=None):
        if comms is None:
            comms = dosa.Comms()

        self.comms = comms

    def run(self, play):
        payload = self.comms.build_payload(dosa.Messages.PLAY, play.encode())

        print("RUN PLAY > " + play)
        if self.comms.send(payload, wait_for_ack=True):
            print("Play request acknowledged.")
        else:
            print()
