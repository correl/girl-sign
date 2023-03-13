import time

from machine import Pin

D1 = 5
D2 = 4
D3 = 0
D4 = 2
D5 = 14


class Girl:
    def __init__(
        self, p_g: int = D1, p_i: int = D2, p_r: int = D3, p_l: int = D5
    ) -> None:
        self.pins = [
            Pin(p_g, Pin.OUT),
            Pin(p_i, Pin.OUT),
            Pin(p_r, Pin.OUT),
            Pin(p_l, Pin.OUT),
        ]
        for pin in self.pins:
            pin.off()

    def show(self, text: str) -> None:
        for pin, value in zip(
            self.pins,
            [
                int("g" in text),
                int("i" in text),
                int("r" in text),
                int("l" in text),
            ],
        ):
            pin.value(value)

    def on(self) -> None:
        for pin in self.pins:
            pin.on()

    def off(self) -> None:
        for pin in self.pins:
            pin.off()


separate = [
    "g",
    "",
    "i",
    "",
    "r",
    "",
    "l",
    "",
]

flash = [
    "girl",
    "",
    "girl",
    "",
    "girl",
    "",
]
gradual = [
    "g",
    "gi",
    "gir",
    "girl",
    "",
]

sign = Girl(D1, D2, D3, D5)

while True:
    for pattern in [separate, flash, gradual, gradual, flash]:
        for state in pattern:
            sign.show(state)
            time.sleep(0.5)
