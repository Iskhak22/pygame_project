class UndoStack:
    def __init__(self):
        # We use a simple Python list as the backing structure for the Stack (LIFO)
        self._stack = []

    def push_state(self, x, y):
        """Pushes the current player (x, y) coordinates before movement."""
        self._stack.append((x, y))

    def pop_state(self):
        """Pops the last (x, y) coordinates from the stack. Returns None if empty."""
        if self._stack:
            return self._stack.pop()
        return None