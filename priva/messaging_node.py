from node import Node

class MessagingNode (Node):
    def __init__(self, ipaddr, port, name, id=None, callback=None, max_connections=0):
        super(MessagingNode, self).__init__(ipaddr, port, name, id, callback, max_connections)

    # todo
    def join():
        return