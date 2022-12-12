import requests
import random
import hashlib
import threading

m = 10 # number of bits in the node ID, and the number of entries in the finger table
s = 2**m # size of the ring

# tor proxies
proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
}

class ChordNode():
    def __init__(self, onion_addr):
        # basic variables
        self.terminate_flag = threading.Event() # Flag to indicate node termination
        self.onion_addr = onion_addr
        self.next = 0

        # state variables
        self.predecessor = None
        self.finger_nodes = {}
        self.finger_table = []
        self.msg_history = dict()

    def set_node_name(self, name):
        self.name = name
        self.user_id = name + '#' + str(random.randint(1, 999999))
        self.node_id = self.get_node_id(self.user_id)

    def get_node_id(self, user_id: str):
        hash = hashlib.blake2b(digest_size=m)
        hash.update(user_id.encode('utf-8'))
        node_id = int(hash.hexdigest(), 16)
        return node_id

    def node_info(self):
        print('\n=========')
        print('name: {}'.format(self.name))
        print('user_id: {}'.format(self.user_id))
        print('node_id: {}'.format(self.node_id))
        print('onion_addr: {}'.format(self.onion_addr))
        print('=========\n')

    def node_test(self):
        print(requests.get('http://{}/find_successor?succ_node_id={}'.format(self.onion_addr, 'test_node_id'), proxies=proxies).text)

    def find_successor(self, node_id):
        if node_id in self.finger_table:
            return self.finger_nodes[node_id]
        closest = self.finger_nodes[self.closest_preceeding_node(node_id)]
        successor = requests.get('http://{}/find_successor?succ_node_id={}'.format(closest['IP'], node_id), proxies)
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
            response = requests.post('http://{}/join'.format(address['IP']), json={'node_id': self.node_id, "address": self.onion_addr}, proxies=proxies)
            successor = response.json()
            self.finger_table.append(successor['node_id'])
            self.finger_nodes[successor['node_id']] = successor
        else:
            self.finger_table.append(self.node_id)
            self.finger_nodes[self.node_id] = self.address

    def stabilize(self):
        """Stabilize the network"""
        successor = self.finger_nodes[self.finger_table[0]]
        response = requests.get('http://{}/get_predecessor'.format(successor['IP']), proxies=proxies)
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
        requests.post('http://{}/notify'.format(node['IP']), json={'node_id': self.node_id, "address": self.onion_addr}, proxies=proxies)
    
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
        response = requests.get('http://{}/ping'.format(self.predecessor['IP']), proxies=proxies)
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
