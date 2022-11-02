# A single node

class Node:
    def __init__(self, data=None, next=None):
        '''Default values in the init class
        With no methods and two attributes'''
        self.data = data
        self.next = next


# Linked list class is a collection of Nodes
class LinkedList:
    def __init__(self):
        # Need to know where headpoint is
        # Create a head value which is None
        self.head = None
    
    # Need to method to insert a new item
    def insert(self, data):
        # Create a new node and insert data
        newnode = Node(data)

            # If head already has a value just insert
        if (self.head):
            current = self.head
            while(current.next): # While there is another item following
                current = current.next
            current.next = newnode

                    # If this is the first item in the list
        else:
            self.head = newnode

    def PrintLL(self):
        current = self.head
        while(current):
            print(current.data)
            current = current.next


# Create a list, add data and display it.  
def process_linked_list():
    LL = LinkedList()
# Add nodes to the empty structure
    LL.insert(10)
    LL.insert(20)
    LL.insert(30)
    LL.PrintLL()
    return LL