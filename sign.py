import time

from machine import Pin

D1 = 5
D2 = 4
D3 = 0
D4 = 2
D5 = 14
D6 = 12


class Girl:
    letters = list("GIRL")

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
                int("G" in text),
                int("I" in text),
                int("R" in text),
                int("L" in text),
            ],
        ):
            pin.value(value)

    def on(self) -> None:
        for pin in self.pins:
            pin.on()

    def off(self) -> None:
        for pin in self.pins:
            pin.off()


def chain(iterators):
    for iterator in iterators:
        yield from iterator


def cycle(iterator):
    while True:
        yield from iterator


def repeat(value):
    while True:
        yield value


class Button:
    DEBOUNCE_DELAY = 50

    def __init__(self, pin, inverted=True):
        self.pin = pin
        self.inverted = inverted
        self._pressed = False
        self._just_changed = False
        self._last_checked = None

    def update(self):
        self._just_changed = False
        now = time.ticks_ms()
        value = bool(self.pin.value())
        if self.inverted:
            value = not value
        if value != self._pressed:
            if self._last_checked is None:
                self._last_checked = time.ticks_ms()
            elif time.ticks_diff(now, self._last_checked) > self.DEBOUNCE_DELAY:
                self._pressed = not self._pressed
                self._last_checked = None
                self._just_changed = True
        elif time.ticks_diff(now, self._last_checked) > self.DEBOUNCE_DELAY:
            self.last_checked = None

    def pressed(self):
        return self._pressed and self._just_changed

    def released(self):
        return not self._pressed and self._just_changed


class App:
    MODE_STATIC = "static"
    MODE_FLASH = "flash"
    MODE_SEPARATE = "separate"
    MODE_GRADUAL = "gradual"
    MODE_COMBINED = "combined"

    def __init__(self):
        self.sign = Girl(D1, D2, D3, D5)
        self.mode_button = Button(Pin(D6, Pin.IN, Pin.PULL_UP), inverted=True)
        self.modes = cycle(
            [
                self.MODE_STATIC,
                self.MODE_FLASH,
                self.MODE_SEPARATE,
                self.MODE_GRADUAL,
                self.MODE_COMBINED,
            ]
        )

    @property
    def pattern_static(self):
        return [self.sign.letters]

    @property
    def pattern_flash(self):
        return list(chain(zip(self.pattern_static, repeat(""))))

    @property
    def pattern_separate(self):
        return self.sign.letters + [""]

    @property
    def pattern_gradual(self):
        seq = [self.sign.letters[: i + 1] for i in range(len(self.sign.letters))]
        return seq + [""]

    @property
    def pattern_combined(self):
        return list(
            chain(
                [
                    self.pattern_separate * 2,
                    self.pattern_flash * 3,
                    self.pattern_gradual * 2,
                    self.pattern_flash * 3,
                ]
            )
        )

    def set_mode(self, mode):
        self.mode = mode
        if mode == self.MODE_STATIC:
            self.states = cycle(self.pattern_static)
        elif mode == self.MODE_FLASH:
            self.states = cycle(self.pattern_flash)
        elif mode == self.MODE_SEPARATE:
            self.states = cycle(self.pattern_separate)
        elif mode == self.MODE_GRADUAL:
            self.states = cycle(self.pattern_gradual)
        elif mode == self.MODE_COMBINED:
            self.states = cycle(self.pattern_combined)
        else:
            return
        self.mode = mode
        print(f"[mode] mode='{mode}'")
        self.update()

    def update(self, delay=500):
        self.state = next(self.states)
        self.delay = delay
        print(f"[update] state='{self.state}', delay={self.delay}")
        self.sign.show(self.state)
        self.last_update = time.ticks_ms()

    def tick(self):
        self.mode_button.update()
        if self.mode_button.released():
            # Was just released
            self.set_mode(next(self.modes))
        if time.ticks_diff(time.ticks_ms(), self.last_update) > self.delay:
            self.update()

    def run(self):
        print("Starting application loop")
        self.set_mode(next(self.modes))
        while True:
            self.tick()
            time.sleep_ms(0)


if __name__ == "__main__":
    app = App()
    app.run()
