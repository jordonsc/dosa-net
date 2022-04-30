import time
import dosa
import struct

from dosa.device import DeviceType, Device

from rich.console import Console
from rich.layout import Layout
from rich.text import Text
from rich.live import Live


class GuiConfig:
    def __init__(self, comms=None):
        if comms is None:
            comms = dosa.Comms()

        self.comms = comms
        self.device_count = 0
        self.devices = []

        self.console = Console()
        self.layout = Layout()

        self.layout.split(
            Layout(name="R1"),
            Layout(name="R2"),
        )

        self.layout["R1"].update(
            Text(
                "foo",
                style="bold black on white",
                justify="center",
            )
        )

    def run(self):
        with Live(self.layout, screen=True, redirect_stderr=False) as live:
            while True:
                pass
