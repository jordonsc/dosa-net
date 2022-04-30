import pathlib
import json

from dosa.exc import *
from dosa.comms import Messages, Message, Comms
from dosa.legacy import Config
from dosa.cfg import GuiConfig
from dosa.monitor import Monitor
from dosa.ping import Ping
from dosa.trigger import Trigger
from dosa.ota import Ota
from dosa.flush import Flush
from dosa.play import Play
from dosa.device import DeviceType, DeviceStatus, Device


class LogLevel:
    DEBUG = 10
    INFO = 20
    STATUS = 30
    WARNING = 40
    ERROR = 50
    CRITICAL = 60

    @staticmethod
    def as_string(log_level):
        if log_level == LogLevel.DEBUG:
            return "DEBUG"
        elif log_level == LogLevel.INFO:
            return "INFO"
        elif log_level == LogLevel.STATUS:
            return "STATUS"
        elif log_level == LogLevel.WARNING:
            return "WARNING"
        elif log_level == LogLevel.ERROR:
            return "ERROR"
        elif log_level == LogLevel.CRITICAL:
            return "CRITICAL"
        else:
            return "UNKNOWN"


class SecurityLevel:
    ALERT = 0
    BREACH = 1
    TAMPER = 2
    PANIC = 3

    @staticmethod
    def as_string(sec_level):
        if sec_level == SecurityLevel.ALERT:
            return "ALERT"
        elif sec_level == SecurityLevel.BREACH:
            return "BREACH"
        elif sec_level == SecurityLevel.TAMPER:
            return "TAMPER"
        elif sec_level == SecurityLevel.PANIC:
            return "PANIC"
        else:
            return "UNKNOWN"


class LockLevel:
    UNLOCKED = 0
    LOCKED = 1
    ALERT = 2
    BREACH = 3

    @staticmethod
    def as_string(lock_level):
        if lock_level == LockLevel.UNLOCKED:
            return "UNLOCKED"
        elif lock_level == LockLevel.LOCKED:
            return "LOCKED"
        elif lock_level == LockLevel.ALERT:
            return "ALERT"
        elif lock_level == LockLevel.BREACH:
            return "BREACH"
        else:
            return "UNKNOWN"


class AlertCategory:
    SECURITY = "Security"
    NETWORK = "Network"


class MessageLog:
    def __init__(self, max_history=25):
        self.history = []
        self.max_history = max_history

    def validate(self, dvc, msg_id):
        if self.is_registered(dvc, msg_id):
            return True
        else:
            self.add_device(dvc, msg_id)
            return False

    def is_registered(self, dvc, msg_id):
        for d, m in self.history:
            if dvc.address == d.address and m == msg_id:
                return True

        return False

    def add_device(self, dvc, msg_id):
        if dvc.address is None:
            return

        if len(self.history) == self.max_history:
            self.history.pop(0)

        self.history.append((dvc, msg_id))


def get_config_file():
    home_file = pathlib.Path(pathlib.Path.home(), ".dosa", "config")
    system_file = pathlib.Path("/", "etc", "dosa", "config")

    if home_file.exists() and home_file.is_file():
        return home_file
    elif system_file.exists() and system_file.is_file():
        return system_file
    else:
        return None


def get_config():
    cfg_file = get_config_file()

    if cfg_file is None:
        return {}
    else:
        print("Load config from " + str(cfg_file) + "..")
        try:
            return json.load(cfg_file.open('r'))
        except json.decoder.JSONDecodeError as e:
            print("ERROR: Failed to parse configuration: " + str(e))
            return {}
