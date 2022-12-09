from hmac import digest_size
import requests
import random
import hashlib
import threading
import socket
import json
import sys
import ipaddress
import stun

m = 10 # number of bits in the node ID, and the number of entries in the finger table
s = 2**m # size of the ring

class ChordNode(threading.Thread):
    # Python class constructor
    def __init__(self, local_port, name):
        super(ChordNode, self).__init__(port, name)
        # basic variables
        self.terminate_flag = threading.Event() # Flag to indicate node termination
        self.name = name
        self.user_id = name + '#' + str(random.randint(1, 999999))
        self.node_id = self.get_node_id(self.user_id)
        self.loc_address = self.get_local_address(local_port)
        self.pub_address = self.get_public_address()
        self.finger_table = []
        self.predecessor = None
        self.finger_nodes = {}
        self.next = 0

        # state variables
        self.msg_history = dict()

        # connection varaibles
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.loc_address['IP'], self.loc_address['port']))
        self.sock.listen()

    def get_local_address(self, local_port):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return {'IP': local_ip, 'port': local_port}

    def get_public_address(self):
        _, pub_ip, pub_port = stun.get_ip_info()
        return {'IP': pub_ip, 'port': pub_port}

    def get_node_id(self, user_id: str):
        hash = hashlib.blake2b(digest_size=m)
        hash.update(user_id.encode('utf-8'))
        node_id = int(hash.hexdigest(), 16)
        return node_id

    def find_successor(self, node_id):
        if node_id in self.finger_table:
            return self.finger_nodes[node_id]
        closest = self.finger_nodes[self.closest_preceeding_node(node_id)]
        successor = requests.get('http://{}:{}/find_successor'.format(closest['IP'], closest['port']))
        return successor

    def in_range(self, a, b, c):
        a = a % s
        b = b % s
        c = c % s
        print(a, b, c)
        if b in range(a, c) or b in range(c, a):
            return True
        return False

    def closest_preceeding_node(self, nodeId: int):
        ft = self.finger_table
        for i in range(len(ft)-1, 0, -1):
            if self.in_range(self.node_id, ft[i], nodeId):
                return ft[i]
        return ft[0] # if no node in range, return the successor

    def join(self, address = None):
        """Join the network"""
        if address:
            response = requests.get('http://{}:{}/find_successor'.format(address['IP'], address['port']))
            successor = response.json()
            self.finger_table.append(successor['node_id'])
            self.finger_nodes[successor['node_id']] = successor
        else:
            self.finger_table.append(self.node_id)
            self.finger_nodes[self.node_id] = self.address

    def stabilize(self):
        """Stabilize the network"""
        successor = self.finger_nodes[self.finger_table[0]]
        response = requests.get('http://{}:{}/get_predecessor'.format(successor['IP'], successor['port']))
        predecessor = response.json()
        # is the successors predecessor in between me and my successor
        if predecessor and self.in_range(self.node_id, predecessor['node_id'], successor['node_id']):
            # if so, set my successor to the successors predecessor
            self.finger_table[0] = predecessor['node_id']
            self.finger_nodes[predecessor['node_id']] = predecessor
        # otherwise notify the successor that i am its predecessor
        self.notify(self.finger_nodes[self.finger_table[0]])

    def notify(self, node):
        """Notify the node"""
        requests.post('http://{}:{}/notify'.format(node['IP'], node['port']), json={'node_id': self.node_id, "address": self.address})
    
    def ack_notify(self, node_id, address):
        """Acknowledge the notification"""
        if not self.predecessor or self.in_range(self.predecessor['node_id'], node_id, self.node_id):
            self.predecessor = {'node_id': node_id, 'address': address}

    def fix_fingers(self):
        """Fix the fingers"""
        self.next = self.next + 1
        if self.next >= m:
            self.next = 1
        self.finger_table[self.next] = self.find_successor(self.node_id + 2**(self.next-1))

    def check_predecessor(self):
        """Check the predecessor"""
        if not self.predecessor:
            return
        response = requests.get('http://{}:{}/ping'.format(self.predecessor['IP'], self.predecessor['port']))
        if response.status_code != 200:
            self.predecessor = None

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
