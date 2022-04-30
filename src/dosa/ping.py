import dosa
import time


class Ping:
    def __init__(self, comms=None):
        if comms is None:
            comms = dosa.Comms()

        self.comms = comms

    def run(self, target):
        ping = self.comms.build_payload(dosa.Messages.PING)
        print("PING > " + target + ":6901")
        self.comms.send(ping, (target, 6901))

        timeout = 1.5
        start_time = time.perf_counter()

        while time.perf_counter() - start_time < timeout:
            msg = self.comms.receive(timeout=timeout)

            if msg is None or msg.msg_code != dosa.Messages.PONG:
                continue

            if msg is None:
                continue

            if msg is not None and msg.msg_code == dosa.Messages.PONG:
                self.print_details(msg)
                return

        print("No reply")

    def print_details(self, msg):
        dvc_type = msg.payload[self.comms.BASE_PAYLOAD_SIZE]
        dvc_state = msg.payload[self.comms.BASE_PAYLOAD_SIZE + 1]

        print("PONG < " + msg.addr[0] + ":" + str(msg.addr[1]) + " (" + msg.device_name + ") // " +
              dosa.device.device_type_str(dvc_type) + "::" + dosa.device.device_status_str(dvc_state))
