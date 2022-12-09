from chord_node import ChordNode

class MessagingNode (ChordNode):
    def __init__(self, ip_addr, port, name, id=None, callback=None, max_connections=0):
        super(MessagingNode, self).__init__(ip_addr, port, name, id, callback, max_connections)

    # todo
    def join():
        return