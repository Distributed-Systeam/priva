from chord_node import ChordNode

class BootstrapNode (ChordNode):
    def __init__(self, ip_addr, port, name, id=None, callback=None, max_connections=0):
        super(BootstrapNode, self).__init__(ip_addr, port, name, id, callback, max_connections)

    def ack_join(self, address, node_id):
        """Send the successor for new joining node"""
        successor = self.find_successor(node_id)
        self.connect_with_node(address['IP'], address['port'])
        new_node = self.nodes_outbound[-1]
        self.send_to_node(new_node, successor)
        self.disconnect_with_node(new_node)
