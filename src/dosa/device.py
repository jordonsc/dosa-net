import time


class DeviceType:
    UNKNOWN = 0
    MONITOR = 1
    UTILITY = 2
    ALARM = 3
    IR_PASSIVE = 10
    IR_ACTIVE = 11
    OPTICAL = 12
    SONAR = 20
    BUTTON = 40
    TOGGLE = 41
    POWER_TOGGLE = 110
    MOTOR = 112
    LIGHT = 113

    @staticmethod
    def as_string(x):
        if x == DeviceType.MONITOR:
            return "Monitor"
        if x == DeviceType.UTILITY:
            return "Utility"
        if x == DeviceType.ALARM:
            return "Alarm"
        elif x == DeviceType.IR_PASSIVE:
            return "PIR Sensor"
        elif x == DeviceType.IR_ACTIVE:
            return "Laser Sensor"
        elif x == DeviceType.OPTICAL:
            return "Optical Sensor"
        elif x == DeviceType.SONAR:
            return "Sonar Sensor"
        elif x == DeviceType.BUTTON:
            return "Push Button"
        elif x == DeviceType.TOGGLE:
            return "Toggle Switch"
        elif x == DeviceType.POWER_TOGGLE:
            return "Power Toggle"
        elif x == DeviceType.MOTOR:
            return "Motorised Winch"
        elif x == DeviceType.LIGHT:
            return "Light Controller"
        else:
            return "Unknown (" + str(x) + ")"


class DeviceStatus:
    OK = 0
    ACTIVE = 1
    MINOR_FAULT = 10
    MAJOR_FAULT = 11
    CRITICAL = 12

    @staticmethod
    def as_string(x):
        if x == DeviceStatus.OK:
            return "OK"
        elif x == DeviceStatus.ACTIVE:
            return "ACTIVE"
        elif x == DeviceStatus.MINOR_FAULT:
            return "MINOR FAULT"
        elif x == DeviceStatus.MAJOR_FAULT:
            return "MAJOR FAULT"
        elif x == DeviceStatus.CRITICAL:
            return "CRITICAL"
        else:
            return "UNKNOWN STATE"


class Device:
    def __init__(self, msg=None, device_type=None, device_state=None):
        if msg:
            self.device_name = msg.device_name
            self.address = msg.addr
            self.msg = msg
        else:
            self.device_name = None
            self.address = None
            self.msg = None

        self.device_type = device_type
        self.device_state = device_state
        self.last_seen = 0
        self.reported_unresponsive = False

        self.pong()

    def pong(self):
        self.last_seen = time.perf_counter()

    def is_stale(self, age=35):
        return time.perf_counter() - self.last_seen > age
