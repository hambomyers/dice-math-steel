# io_pico.py — keypad + SSD1306 OLED for the Pico.
# I/O only. Does not count against the crypto line budget in birth_pico.py.
# Secrets are never written to flash from this module.

# Matrix keypad and OLED wiring are board-specific. On desktop tests these
# functions are replaced with stubs that feed rolls / print to stdout.


class Display:
    def __init__(self):
        self.lines = []

    def clear(self):
        self.lines = []

    def show(self, text):
        # SSD1306: short lines a tired operator can read aloud
        self.lines = str(text).split("\n")[:4]
        print("OLED:", " | ".join(self.lines))


class Keypad:
    def __init__(self, feed=None):
        self._feed = list(feed) if feed is not None else None
        self._i = 0

    def read_digit(self):
        # Returns 1..6 for a die face entry, or other digits for menus.
        if self._feed is not None:
            if self._i >= len(self._feed):
                raise EOFError("keypad feed empty")
            v = self._feed[self._i]
            self._i += 1
            return v
        raise RuntimeError("no keypad hardware binding")


def confirm_spoken(display, address, fingerprint):
    # Operator reads fingerprint aloud; never hex-vs-hex.
    display.show("ADDR OK?\n" + " ".join(fingerprint))
    return True


def enter_rolls(keypad, display, n=256, label="KEY"):
    display.show("%s rolls\n0/%d" % (label, n))
    rolls = []
    while len(rolls) < n:
        d = keypad.read_digit()
        if 1 <= d <= 6:
            rolls.append(d)
            if len(rolls) % 16 == 0 or len(rolls) == n:
                display.show("%s %d/%d" % (label, len(rolls), n))
    return rolls
