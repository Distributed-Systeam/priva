import hashlib
import random
from node import Node

class BootstrapNode (Node):
    def __init__(self, ipaddr, port, name, id=None, callback=None, max_connections=0):
        super(BootstrapNode, self).__init__(ipaddr, port, name, id, callback, max_connections)

    def ack_join(self, ipaddr, port, name):
        """Generates a unique ID for each messaging node."""
        node_id = hashlib.sha512()
        user_id = name + '#' + str(random.randint(1, 999999))
        node_id.update(user_id.encode('ascii'))
        node_id = node_id.hexdigest()
        details = dict()
        details['node_id'] = node_id
        details['user_id'] = user_id
        return details
