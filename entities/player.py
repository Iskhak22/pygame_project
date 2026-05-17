class Player:
    def __init__(self, x, y):
        self.name = ""
        self.x = x
        self.y = y
        self.hp = 100
        self.money = 0
        self.exp = 0
        self.has_gun = False

    def set_position(self, x, y):
        self.x, self.y = x, y