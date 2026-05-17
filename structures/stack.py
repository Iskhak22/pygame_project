import copy

class UndoStack:
    def __init__(self):
        self.items = []

    def push_state(self, x, y, map_data):
        self.items.append({'x': x, 'y': y, 'map': copy.deepcopy(map_data)})

    def pop_state(self):
        return self.items.pop() if self.items else None