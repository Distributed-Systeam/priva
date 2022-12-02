import time
from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection
import random
import hashlib

class Node (Node):
    # Python class constructor
    def __init__(self, ipaddr, port, name, id=None, callback=None, max_connections=0):
        super(Node, self).__init__(ipaddr, port, id, callback, max_connections)
        self.name = name
        self.user_id = name + '#' + str(random.randint(1, 999999))
        self.node_id = self.get_node_id(self.user_id)
        self.address = {
            'IP': ipaddr,
            'port': port
        }
        self.finger_table = []
        self.predecessor = None

    def get_node_id(self, user_id):
        node_id = hashlib.sha512()
        node_id.update(user_id.encode('ascii'))
        node_id = node_id.hexdigest()
        return node_id

    def get_successor(self, node_id):
        # TODO: retun successor (address object) of node_id
        return None

    def init_conn(self, user_id):
        nodeID = hash(user_id) # hash the user_id to get a unique nodeID
        closest = self.closest_preceeding_node(self.node_id) # check finger table
        if (closest == nodeID):
            #connect with node
            pass
        self.connect_with_node(closest.ipaddr, closest.port) # connect to the closest node
        self.send_to_node(closest, "I want to connect with nodeID", "my address info")
        self.disconnect_with_node(closest)

    def msg_conn(self, node_id, node):
        """This method is called when a node wants to connect with another node."""
        #if Node in finger_tbl: # check if the node is already in the finger table
          #  Node.node_id.node_msg(Node,Data)
        #else:
         #   max_finger_tbl = fingler_tbl[0] # get the first node in the finger table
        #    max_finger_tbl.rote_conn(node_id, Node)
      #  pass

    def closest_preceeding_node(self, nodeId):
        """Returns the closest node in the finger table that precedes the given nodeID."""
        #for i in range(160, 0, -1):
        #    if (fingerTable[i].nodeId < nodeId and fingerTable[i].nodeId > self.nodeId):
        #        return fingerTable[i] # Node element
        return 
    
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
