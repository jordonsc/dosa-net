class DosaException(Exception):
    pass


class CommsException(DosaException):
    pass


class NotDosaPacketException(CommsException):
    pass
