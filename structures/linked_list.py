class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def add_item(self, item):
        new_node = Node(item)
        new_node.next = self.head
        self.head = new_node

    def get_all(self):
        items = []
        curr = self.head
        while curr:
            items.append(curr.data)
            curr = curr.next
        return items