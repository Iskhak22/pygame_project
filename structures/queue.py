class QueueNode:
    def __init__(self, entity):
        self.entity = entity
        self.next = None

class TurnQueue:
    def __init__(self):
        self.front = None
        self.rear = None

    def enqueue(self, entity):
        new_node = QueueNode(entity)
        if self.rear is None:
            self.front = self.rear = new_node
            return
        self.rear.next = new_node
        self.rear = new_node

    def dequeue(self):
        if self.front is None:
            return None
        temp = self.front
        self.front = temp.next
        if self.front is None:
            self.rear = None
        return temp.entity