import dosa
import struct
import time


class Monitor:
    def __init__(self, comms=None, ignore=False, ack=False, map=False, ignore_pings=False):
        if comms is None:
            comms = dosa.Comms()

        self.last_msg_id = 0
        self.comms = comms
        self.ignore_retries = ignore
        self.auto_ack = ack
        self.print_map = map
        self.ignore_pings = ignore_pings
        self.history = dosa.MessageLog()

    def run(self):
        while True:
            msg = self.comms.receive(timeout=None)
            aux = ""

            device = dosa.Device(msg=msg)
            is_retry = self.history.validate(device, msg.msg_id)

            if self.ignore_retries and is_retry:
                continue

            if self.ignore_pings and (msg.msg_code == dosa.Messages.PING):
                continue

            if msg.msg_code == dosa.Messages.ACK:
                continue
            elif msg.msg_code == dosa.Messages.TRIGGER and not is_retry:
                if self.auto_ack:
                    self.comms.send_ack(msg.msg_id_bytes(), msg.addr)
                    aux += " (replied)"
                if self.print_map:
                    trigger_type = struct.unpack("<B", msg.payload[27:28])[0]
                    if trigger_type == 3:
                        # Ranging sensor, show distances
                        dist_prev = struct.unpack("<H", msg.payload[28:30])[0]
                        dist_new = struct.unpack("<H", msg.payload[30:32])[0]
                        aux += " // distance: " + str(dist_prev) + " -> " + str(dist_new)
                    elif trigger_type == 4:
                        # IR grid, display map
                        aux += "\n+--------+\n"
                        index = 0
                        for row in range(8):
                            aux += "|"
                            for col in range(8):
                                aux += self.print_pixel(struct.unpack("<B", msg.payload[28 + index:29 + index])[0])
                                index += 1
                            aux += "|\n"
                        aux += "+--------+"
            elif msg.msg_code == dosa.Messages.LOG:
                log_level = struct.unpack("<B", msg.payload[27:28])[0]
                log_message = msg.payload[28:msg.payload_size].decode("utf-8")
                aux = " // [" + dosa.LogLevel.as_string(log_level) + "] " + log_message
            elif msg.msg_code == dosa.Messages.SEC:
                sec_level = struct.unpack("<B", msg.payload[27:28])[0]
                aux = " // SECURITY ALERT: " + dosa.SecurityLevel.as_string(sec_level)
            elif msg.msg_code == dosa.Messages.PLAY:
                play = msg.payload[27:msg.payload_size].decode("utf-8")
                aux = " // RUN PLAY: " + play
            elif msg.msg_code == dosa.Messages.ONLINE:
                aux = " // ONLINE"
            elif msg.msg_code == dosa.Messages.BEGIN:
                aux = " // BEGIN SEQUENCE"
            elif msg.msg_code == dosa.Messages.END:
                aux = " // COMPLETE"
            elif msg.msg_code == dosa.Messages.PING:
                aux = " // PING"
            elif msg.msg_code == dosa.Messages.PONG:
                aux = " // PONG"
            elif msg.msg_code == dosa.Messages.FLUSH:
                aux = " // FLUSH"

            # Timestamp of message
            t = time.strftime("%H:%M:%S", time.localtime())

            print(t + " [" + str(msg.msg_id).rjust(5, ' ') + "] " + msg.addr[0] + ":" + str(msg.addr[1]) +
                  " (" + msg.device_name + "): " + msg.msg_code.decode("utf-8") + aux)

            self.last_msg_id = msg.msg_id

    @staticmethod
    def print_pixel(p):
        if p == 0:
            return " "

        p = p / 10
        if p > 3:
            return "#"
        elif p > 1.5:
            return "+"
        else:
            return "."
