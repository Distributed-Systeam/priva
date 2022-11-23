import time
from p2pnetwork.node import Node

class Node (Node):
    # Python class constructor
    def __init__(self, ipaddr, port, name, id=None, callback=None, max_connections=0):
        super(Node, self).__init__(ipaddr, port, id, callback, max_connections)
        self.name = name

    def outbound_node_connected(self, connected_node):
        print("outbound_node_connected: " + connected_node.id)
        
    def inbound_node_connected(self, connected_node):
        print("inbound_node_connected: " + connected_node.id)

    def inbound_node_disconnected(self, connected_node):
        print("inbound_node_disconnected: " + connected_node.id)

    def outbound_node_disconnected(self, connected_node):
        print("outbound_node_disconnected: " + connected_node.id)

    def node_message(self, connected_node, data):
        print("node_message from " + connected_node.id + ": " + str(data))
        
    def node_disconnect_with_outbound_node(self, connected_node):
        print("node wants to disconnect with oher outbound node: " + connected_node.id)
        
    def node_request_to_stop(self):
        print("node is requested to stop!")

    def send_ping(self):
        """A ping request is send to all the nodes that are connected."""
        self.send_to_nodes(self.create_message( {'_type': 'ping', 'timestamp': time.time(), 'id': self.id} ))

    def send_pong(self, node, timestamp):
        """A pong request is only send to the node that has send the ping request."""
        node.send(self.create_message( {'_type': 'pong', 'timestamp': timestamp, 'timestamp_node': time.time(), 'id': self.id} ))

    def create_message(self, data):
        """This method creates the message based on the Python dict data variable to be sent to other nodes. Some data
           is added to the data, like the id, timestamp, message is and hash of the message. In order to check the
           message validity when a node receives it, the message is hashed and signed. The method returns a string
           of the data in JSON format, so it can be send immediatly to the node. The public key is also part of the
           communication packet."""
        for el in ['_id', '_timestamp', '_message_id', '_hash', '_signature', '_public_key']: # Clean up the data, to make sure we calculatie the right things!
            if ( el in data ):
                del data[el]

        try:
            data['_mcs']        = self.message_count_send
            data['_mcr']        = self.message_count_recv
            data['_id']         = self.id
            data['_timestamp']  = time.time()
            data['_message_id'] = self.get_hash(data)

            self.debug_print("Message creation:")
            self.debug_print("Message hash based on: " + self.get_data_uniq_string(data))

            data['_hash']       = self.get_hash(data)

            self.debug_print("Message signature based on: " + self.get_data_uniq_string(data))

            data['_signature']  = self.sign_data(data)
            data['_public_key'] = self.get_public_key().decode('utf-8')

            self.debug_print("_hash: " + data['_hash'])
            self.debug_print("_signature: " + data['_signature'])
            self.debug_print("_public_key: " + data['_public_key'])

            return data

        except Exception as e:
            self.debug_print("SecureNode: Failed to create message " + str(e))
