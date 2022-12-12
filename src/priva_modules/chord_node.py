import requests
import random
import hashlib
import threading
import json

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
        self.predecessor = None # dict of predecessor node (node_id: onion_addr)
        self.finger_nodes = {} # dict of finger nodes (node_id: onion_addr)
        self.finger_table = [0] * m # list of finger node ids
        self.msg_history = dict()

    def set_node_name(self, name):
        self.name = name
        self.user_id = name + '#' + str(random.randint(1, 999999))
        self.node_id = self.get_node_id(self.user_id)
        if name == 'boot0':
            self.update_fingertable(self.node_id, self.onion_addr)

    def update_fingertable(self, node_id, onion_addr, index=0):
        self.finger_table[index] = node_id
        self.finger_nodes[node_id] = onion_addr

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
        if len(self.finger_nodes) == 1:
            return json.dumps({
                "node_id": self.finger_table[0],
                "onion_addr": self.finger_nodes[self.finger_table[0]]
            })
        if node_id in self.finger_table:
            return self.finger_nodes[node_id]
        closest_addr = self.finger_nodes[self.closest_preceeding_node(node_id)]
        response = requests.get('http://{}/find_successor?succ_node_id={}'.format(closest_addr, node_id), proxies=proxies)
        successor = json.load(response.json())
        return successor

    def in_range(self, a, b, c):
        a = a % s
        b = b % s
        c = c % s
        return b in range(a, c) or b in range(c, a)

    def closest_preceeding_node(self, node_id: int):
        ft = self.finger_table
        for i in range(len(ft)-1, 0, -1):
            if self.in_range(self.node_id, ft[i], node_id):
                return ft[i]
        return ft[0] # if no node in range, return the successor

    def join(self, onion_addr = None):
        """Join the network"""
        try:
            if onion_addr:
                response = requests.post('http://{}/join'.format(onion_addr), json={'node_id': self.node_id, "onion_addr": self.onion_addr}, proxies=proxies)
                successor = json.load(response.json())
                print(successor)
                self.finger_table.append(successor['node_id'])
                self.finger_nodes[successor['node_id']] = successor['onion_addr']
            else:
                self.finger_table.append(self.node_id)
                self.finger_nodes[self.node_id] = self.onion_addr
            return 'Joined the network'
        except:
            return 'Failed to join the network'

    def stabilize(self):
        """Stabilize the network"""
        succ_id = self.finger_table[0]
        succ_addr = self.finger_nodes[succ_id]
        response = requests.get('http://{}/get_predecessor'.format(succ_addr), proxies=proxies)
        succ_pred = json.load(response.json())
        # is the successors predecessor in between me and my successor
        if succ_pred and self.in_range(self.node_id, succ_pred['node_id'], succ_id):
            # if so, set my successor to the successors predecessor
            self.finger_table[0] = succ_pred['node_id']
            self.finger_nodes[succ_pred['node_id']] = succ_pred['onion_addr']
        else:
            # otherwise notify the successor that i am its predecessor
            self.notify(self.finger_nodes[self.finger_table[0]])

    def notify(self, onion_addr):
        """Notify the node"""
        requests.post('http://{}/notify'.format(onion_addr), json={'node_id': self.node_id, "onion_addr": self.onion_addr}, proxies=proxies)
    
    def ack_notify(self, node_id, onion_addr):
        """Acknowledge the notification"""
        if not self.predecessor or self.in_range(self.predecessor['node_id'], node_id, self.node_id):
            self.predecessor = {'node_id': node_id, 'onion_addr': onion_addr}

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
        response = requests.get('http://{}/ping'.format(self.predecessor['onion_addr']), proxies=proxies)
        if response.status_code != 200:
            self.predecessor = None