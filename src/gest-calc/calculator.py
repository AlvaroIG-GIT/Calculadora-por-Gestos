"""Lógica de la calculadora. No depende de la cámara ni de la interfaz."""

OPERATIONS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
}


class Calculator:
    MAX_DIGITS = 10

    def __init__(self):
        self.reset()

    def reset(self):
        self.left = ""
        self.op = None
        self.right = ""
        self.result = None
        self.error = False

    @staticmethod
    def _fmt(x):
        return f"{x:.8g}"

    def press_digit(self, d):
        if self.result is not None or self.error:
            self.reset()  # tras un resultado, empieza una operación nueva
        attr = "right" if self.op else "left"
        current = getattr(self, attr)
        if len(current) >= self.MAX_DIGITS:
            return
        current = str(d) if current == "0" else current + str(d)
        setattr(self, attr, current)

    def press_op(self, op):
        if self.error:
            return
        if self.result is not None:  # encadenar sobre el resultado anterior
            self.left = self._fmt(self.result)
            self.result, self.right = None, ""
        if not self.left:
            return
        if self.right:  # 2 + 3 + ... evalúa primero 2 + 3
            self.equals()
            if self.error:
                return
            self.left = self._fmt(self.result)
            self.result, self.right = None, ""
        self.op = op

    def equals(self):
        if not (self.left and self.op and self.right):
            return
        a, b = float(self.left), float(self.right)
        if self.op == "/" and b == 0:
            self.error = True
            return
        self.result = OPERATIONS[self.op](a, b)

    def delete(self):
        if self.result is not None or self.error:
            self.reset()
        elif self.right:
            self.right = self.right[:-1]
        elif self.op:
            self.op = None
        else:
            self.left = self.left[:-1]

    @property
    def expression(self):
        return f"{self.left} {self.op or ''} {self.right}".strip()

    @property
    def display(self):
        if self.error:
            return "Error: division por 0"
        if self.result is not None:
            return "= " + self._fmt(self.result)
        return self.right or self.left or "0"
