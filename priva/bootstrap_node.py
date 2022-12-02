from node import Node

class BootstrapNode (Node):
    def __init__(self, ipaddr, port, name, id=None, callback=None, max_connections=0):
        super(BootstrapNode, self).__init__(ipaddr, port, name, id, callback, max_connections)

    def ack_join(self, address, node_id):
        """Send the successor for new joining node"""
        successor = self.get_successor(node_id)
        self.connect_with_node(address['IP'], address['port'])
        new_node = self.nodes_outbound()[-1]
        self.send_to_node(new_node, successor)
        self.disconnect_with_node(new_node)
