import requests
from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection
import random
import hashlib

class ChordNode (Node):
    # Python class constructor
    def __init__(self, ip_addr, port, name, id=None, callback=None, max_connections=0):
        super(ChordNode, self).__init__(ip_addr, port, id, callback, max_connections)
        self.name = name
        self.user_id = name + '#' + str(random.randint(1, 999999))
        self.node_id = self.get_node_id(self.user_id)
        self.address = {
            'IP': ip_addr,
            'port': port
        }
        self.finger_table = []
        self.predecessor = None
        self.finger_nodes = {}

    def get_node_id(self, user_id):
        node_id = hashlib.sha512()
        node_id.update(user_id.encode('ascii'))
        node_id = node_id.hexdigest()
        return node_id

    def find_successor(self, node_id):
        # TODO: retun successor (address object) of node_id
        if node_id in self.finger_table:
            return self.finger_nodes[node_id]
        closest = self.finger_nodes[self.closest_preceeding_node(node_id)]
        successor = requests.get('http://{}:{}/find_successor'.format(closest['IP'], closest['port']))
        return successor

    def init_conn(self, user_id):
        node_id = self.get_node_id(user_id) # hash the user_id to get a unique nodeID
        closest = self.closest_preceeding_node(self.node_id) # check finger table
        if (closest == node_id):
            #connect with node
            pass
        self.connect_with_node(closest.ip_addr, closest.port) # connect to the closest node
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
        ft = self.finger_table
        for i in range(len(ft)-1, 0, -1):
            if self.node_id < ft[i] < nodeId:
                return ft[i]
            if self.node_id > ft[i] > nodeId:
                return ft[i]
        return self.node_id

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
        self.send_to_nodes('ping')
