import time
import dosa
import struct

from dosa.device import DeviceType, Device


class Config:
    def __init__(self, comms=None):
        if comms is None:
            comms = dosa.Comms()

        self.comms = comms
        self.device_count = 0
        self.devices = []

    def run(self, target=None):
        if target is None:
            self.run_scan()
            if len(self.devices) == 0:
                print("No devices detected")
                return

            device = self.user_select_device()
            if device is None:
                return
        else:
            device = Device()
            device.address = (target, 6901)

        opt = self.user_select_opt(device.device_type == DeviceType.UNKNOWN)
        if opt == 1:
            # Debug dump
            self.exec_debug_dump(device)
        elif opt == 2:
            # BT config mode
            self._print_output(
                self.exec_config_mode(device)
            )
        elif opt == 3:
            # Set BT password
            self._print_output(
                self.exec_device_password(device, self.get_values(["New password"]))
            )
        elif opt == 4:
            # Set device name
            self._print_output(
                self.exec_device_name(device, self.get_values(["Device name"]))
            )
        elif opt == 5:
            # Set wifi details
            self._print_output(
                self.exec_wifi_ap(device, self.get_values(["Wifi SSID", "Wifi Password"]))
            )
        elif opt == 6:
            # Device configuration
            if device.device_type == DeviceType.IR_PASSIVE:
                # IR sensor calibration
                print("IR configuration")
                self._print_output(
                    self.exec_sensor_calibration(device, self.get_values(
                        ["Min pixels/trigger (int)", "Single-pixel delta (float)", "Total delta (float)"]
                    ))
                )
            elif device.device_type == DeviceType.SONAR:
                # Sonar sensor calibration (ranging)
                print("Sonar configuration")
                self._print_output(
                    self.exec_ranging_calibration(device, self.get_values(
                        ["Trigger threshold", "Fixed calibration", "Trigger Coefficient"]
                    ))
                )
            elif device.device_type == DeviceType.IR_ACTIVE:
                # Laser sensor calibration (ranging)
                print("Laser configuration")
                self._print_output(
                    self.exec_ranging_calibration(device, self.get_values(
                        ["Trigger threshold", "Fixed calibration", "Trigger Coefficient"]
                    ))
                )
            elif device.device_type == DeviceType.MOTOR:
                # Winch driver calibration
                print("Motorised winch configuration")
                self._print_output(
                    self.exec_door_calibration(device, self.get_values(
                        ["Open distance (mm)", "Open-wait time (ms)", "Cool-down (ms)", "Close ticks (int)"]
                    ))
                )
            elif device.device_type == DeviceType.POWER_TOGGLE:
                # Relay calibration
                print("Relay configuration")
                self._print_output(
                    self.exec_relay_calibration(device, self.get_values(
                        ["Relay activation time"]
                    ))
                )
            else:
                print("Device cannot be configured (" + str(device.device_type) + ")")
                return
        elif opt == 7:
            # Set lock state
            self._print_output(
                self.exec_lock_state(device, self.user_select_lock_state())
            )
        elif opt == 8:
            # Set listen devices
            print("Enter devices, one per line. Ctrl+C to abort, no devices for listen to all:")
            devices = []
            while True:
                d = input("> ")
                if d is None or len(d) == 0:
                    break
                else:
                    devices.append(d)
            self._print_output(
                self.exec_listen_devices(device, devices)
            )
        elif opt == 9:
            # Set stats server
            self._print_output(
                self.exec_stats_server(device, self.get_values(["Stats server address", "Stats server port"]))
            )

    @staticmethod
    def _print_output(out):
        if out:
            print("Update success")
        else:
            print("Failed to update configuration")

    def exec_debug_dump(self, device):
        self.comms.send(self.comms.build_payload(dosa.Messages.DEBUG), tgt=device.address,
                        wait_for_ack=False)

        timeout = 1.0
        start_time = time.perf_counter()
        while time.perf_counter() - start_time < timeout:
            msg = self.comms.receive(timeout=timeout)

            if msg is None or msg.msg_code != dosa.Messages.LOG:
                continue

            if device.device_type == DeviceType.UNKNOWN:
                print("[" + dosa.LogLevel.as_string(struct.unpack("<B", msg.payload[27:28])[0]) + "] " +
                      msg.addr[0].ljust(18) + msg.device_name.ljust(22) +
                      msg.payload[28:msg.payload_size].decode("utf-8"))
            else:
                print("[" + dosa.LogLevel.as_string(struct.unpack("<B", msg.payload[27:28])[0]) + "] " +
                      msg.payload[28:msg.payload_size].decode("utf-8"))

    def exec_config_mode(self, device):
        return self.comms.send(self.comms.build_payload(dosa.Messages.REQUEST_BT_CFG_MODE), tgt=device.address,
                               wait_for_ack=True)

    def exec_device_password(self, device, values):
        if values is None:
            return False

        if 4 > len(values[0]) > 50:
            print("Bad password size (4-50 chars)")
            return False

        aux = bytearray()
        aux[0:1] = struct.pack("<B", 0)
        aux[1:] = values[0].encode()
        return self.comms.send(self.comms.build_payload(dosa.Messages.CONFIG_SETTING, aux), tgt=device.address,
                               wait_for_ack=True)

    def exec_device_name(self, device, values):
        if values is None:
            return False

        if 2 > len(values[0]) > 20:
            print("Bad device name (2-20 chars)")
            return False

        aux = bytearray()
        aux[0:1] = struct.pack("<B", 1)
        aux[1:] = values[0].encode()
        return self.comms.send(self.comms.build_payload(dosa.Messages.CONFIG_SETTING, aux), tgt=device.address,
                               wait_for_ack=True)

    def exec_wifi_ap(self, device, values):
        aux = bytearray()
        aux[0:1] = struct.pack("<B", 2)

        if values is None:
            print("Clearing wifi details..", end="")
            aux[1:] = "\n".encode()
        else:
            print("Sending new wifi details..", end="")
            aux[1:] = (values[0] + "\n" + values[1]).encode()

        return self.comms.send(self.comms.build_payload(dosa.Messages.CONFIG_SETTING, aux), tgt=device.address,
                               wait_for_ack=True)

    def exec_sensor_calibration(self, device, values):
        aux = bytearray()
        aux[0:1] = struct.pack("<B", 3)

        if values is None:
            return False
        else:
            try:
                aux[1:2] = struct.pack("<B", int(values[0]))  # Min pixels
                aux[2:6] = struct.pack("<f", float(values[1]))  # Single delta
                aux[6:10] = struct.pack("<f", float(values[2]))  # Total delta
            except ValueError:
                print("Malformed calibration data, aborting")
                return False

        return self.comms.send(self.comms.build_payload(dosa.Messages.CONFIG_SETTING, aux), tgt=device.address,
                               wait_for_ack=True)

    def exec_door_calibration(self, device, values):
        aux = bytearray()
        aux[0:1] = struct.pack("<B", 4)

        if values is None:
            return False
        else:
            try:
                aux[1:3] = struct.pack("<H", int(values[0]))  # Open distance
                aux[3:7] = struct.pack("<L", int(values[1]))  # Open-wait time (ms)
                aux[7:11] = struct.pack("<L", int(values[2]))  # Cool-down (ms)
                aux[11:15] = struct.pack("<L", int(values[3]))  # Close ticks
            except ValueError:
                print("Malformed calibration data, aborting")
                return False

        return self.comms.send(self.comms.build_payload(dosa.Messages.CONFIG_SETTING, aux), tgt=device.address,
                               wait_for_ack=True)

    def exec_ranging_calibration(self, device, values):
        aux = bytearray()
        aux[0:1] = struct.pack("<B", 5)

        if values is None:
            return False
        else:
            try:
                aux[1:3] = struct.pack("<H", int(values[0]))  # Trigger threshold
                aux[3:5] = struct.pack("<H", int(values[1]))  # Fixed calibration
                aux[5:9] = struct.pack("<f", float(values[2]))  # Trigger coefficient
            except ValueError:
                print("Malformed calibration data, aborting")
                return False

        return self.comms.send(self.comms.build_payload(dosa.Messages.CONFIG_SETTING, aux), tgt=device.address,
                               wait_for_ack=True)

    def exec_relay_calibration(self, device, values):
        aux = bytearray()
        aux[0:1] = struct.pack("<B", 8)

        if values is None:
            return False
        else:
            try:
                aux[1:5] = struct.pack("<L", int(values[0]))  # Relay activation time
            except ValueError:
                print("Malformed relay settings, aborting")
                return False

        return self.comms.send(self.comms.build_payload(dosa.Messages.CONFIG_SETTING, aux), tgt=device.address,
                               wait_for_ack=True)

    def exec_lock_state(self, device, lock_state):
        aux = bytearray()
        aux[0:1] = struct.pack("<B", 6)

        if lock_state is None:
            return False
        else:
            try:
                aux[1:2] = struct.pack("<B", lock_state)  # Lock state
            except ValueError:
                print("Malformed lock data, aborting")
                return False

        return self.comms.send(self.comms.build_payload(dosa.Messages.CONFIG_SETTING, aux), tgt=device.address,
                               wait_for_ack=True)

    def exec_listen_devices(self, device, values):
        aux = bytearray()
        aux[0:1] = struct.pack("<B", 7)
        if len(values) > 0:
            aux[1:] = ("\n".join(values) + "\n").encode()
            print("Sending new device list..")
        else:
            print("Set listen mode to all devices..")

        return self.comms.send(self.comms.build_payload(dosa.Messages.CONFIG_SETTING, aux), tgt=device.address,
                               wait_for_ack=True)

    def exec_stats_server(self, device, values):
        aux = bytearray()
        aux[0:1] = struct.pack("<B", 9)

        if values is None:
            return False
        else:
            try:
                aux[1:3] = struct.pack("<H", int(values[1]))  # Server port
                aux[3:] = values[0].encode()  # Server address
            except ValueError:
                print("Malformed server settings, aborting")
                return False

        return self.comms.send(self.comms.build_payload(dosa.Messages.CONFIG_SETTING, aux), tgt=device.address,
                               wait_for_ack=True)

    @staticmethod
    def get_values(vals):
        """
        Retrieve an array of user inputs.
        """
        r_vals = []
        for v in vals:
            r = input(v + ": ")

            # If the first input value is blank, we'll return None
            if len(r) == 0 and len(r_vals) == 0:
                return None

            r_vals.append(r)

        return r_vals

    def run_scan(self):
        ping = self.comms.build_payload(dosa.Messages.PING)

        retries = 5
        timeout = 0.1
        self.devices = []

        print("Scanning..")

        for attempt in range(retries):
            self.comms.send(ping)
            start_time = time.perf_counter()

            while time.perf_counter() - start_time < timeout:
                msg = self.comms.receive(timeout=timeout)

                if msg is None or msg.msg_code != dosa.Messages.PONG:
                    continue

                for d in self.devices:
                    if d.address[0] == msg.addr[0]:
                        msg = None
                        break

                if msg is None:
                    continue

                d = Device(msg=msg, device_type=msg.payload[self.comms.BASE_PAYLOAD_SIZE],
                           device_state=msg.payload[self.comms.BASE_PAYLOAD_SIZE + 1])
                self.devices.append(d)
                self.device_count += 1

        self.devices.sort(key=lambda x: x.msg.device_name)

        print("\033[F\033[K")
        print("[0]:  <All Devices>")
        for key, d in enumerate(self.devices, start=1):
            spacer = " " if key < 10 else ""
            print("[" + str(key) + "]: " + spacer +
                  d.msg.device_name.ljust(22) +
                  d.msg.addr[0].ljust(18) +
                  dosa.DeviceType.as_string(d.device_type).upper().ljust(20) +
                  dosa.DeviceStatus.as_string(d.device_state))

    def user_select_device(self):
        while True:
            try:
                opt = int(input("> "))
            except ValueError:
                opt = None

            if opt is None:
                return None

            if opt == 0:
                return Device(DeviceType.UNKNOWN, 0, (self.comms.MULTICAST_GROUP, self.comms.MULTICAST_PORT))
            elif 0 < opt <= len(self.devices):
                print()
                return self.devices[opt - 1]
            else:
                print("Invalid device")

    @staticmethod
    def user_select_opt(all_devices=False):
        print("[1] Request debug dump")
        print("[2] Order device into Bluetooth configuration mode")
        print("[3] Set device password")
        print("[4] N/A" if all_devices else "[4] Set device name")
        print("[5] Set wifi configuration")
        print("[6] N/A" if all_devices else "[6] Configure device settings")
        print("[7] Set device lock")
        print("[8] Set listen devices")
        print("[9] Set stats server")

        while True:
            try:
                opt = int(input("> "))
            except ValueError:
                opt = None

            if opt is None or opt == 0:
                return None

            if 0 < opt < 10:
                print()
                return opt
            else:
                print("Invalid option")

    @staticmethod
    def user_select_lock_state():
        print("[1] Unlocked")
        print("[2] Locked")
        print("[3] Locked: alert")
        print("[4] Locked: breach")

        while True:
            try:
                opt = int(input("> "))
            except ValueError:
                opt = None

            if opt is None or opt == 0:
                return None

            if 0 < opt < 5:
                print()
                return opt - 1
            else:
                print("Invalid option")
