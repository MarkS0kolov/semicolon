import mpmath as mp

class PiDigit(int):
    def __new__(cls, startPos, endPos):
        mp.dps = endPos + 5
        startPos = startPos
        endPos = endPos
        pi = mp.nstr(mp.pi, endPos + 1)[1:]
        value = int(pi[startPos - 1 : endPos])
        obj = super().__new__(cls, value)
        obj.startPos = startPos
        obj.end = endPos
        obj.pi = pi
        obj.value = value
        return obj

    def __str__(self):
        return str(self.value)
    def __repr__(self):
        return str(f"PiDigit with startPos - {self.startPos}, endPos - {self.endPos} and value equal to {str(self)}")
