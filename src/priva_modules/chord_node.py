import random
import hashlib
import threading
from dataclasses import dataclass
from typing import List, Union
from priva_modules import services

m = 10 # number of bits in the node ID, and the number of entries in the finger table
s = 2**m # size of the ring

@dataclass
class NodeInfo:
    node_id: int
    onion_addr: str

bootstrap_onion = 'eg76gq2w4dksqejhmf5zdxnof5aqi55yzy6we65r347hp2zzbo24uvqd.onion'

class ChordNode():
    def __init__(self, onion_addr):
        # basic variables
        self.terminate_flag = threading.Event() # Flag to indicate node termination
        self.onion_addr = onion_addr
        self.next = 0

        # state variables
        self.predecessor = None
        self.finger_table: List[NodeInfo] = []
        self.msg_history = dict()
        self.last_message = ''
        self.current_msg_peer = ''

    def set_node_name(self, name):
        self.name = name
        self.user_id = name + '#' + str(random.randint(1, 999999))
        self.node_id = self.get_node_id(self.user_id)

    def set_successor(self, node: NodeInfo):
        ft = self.finger_table
        if len(ft) == 0:
            ft.append(node)
        else:
            ft[0] = node

    def get_successor(self) -> NodeInfo:
        return self.finger_table[0]

    def get_node_id(self, user_id: str) -> int:
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
        print('predecessor: {}'.format(self.predecessor))
        print('successor: {}'.format(self.finger_table[0]))
        print('=========\n')

    def send_connect(self, tag):
        connect_node_hash = self.get_node_id(tag)
        successor = self.find_successor(connect_node_hash)
        if successor.node_id == connect_node_hash:
            res = services.send_connect(successor.onion_addr, self.user_id)
            self.current_msg_peer = res['user_id']
        else:
            print('NODE NOT ALIVE!')

    def get_node_from_ft(self, node_id) -> Union[NodeInfo, None]:
        for node_info in self.finger_table:
            if node_info.node_id == node_id:
                return node_info
        return None

    def node_test(self):
        print(services.test(bootstrap_onion, self.node_id))

    def get_predecessor(self) -> Union[NodeInfo, None]:
        print('PREDERCESSOR: {}'.format(self.predecessor))
        return self.predecessor

    def find_successor(self, node_id: int) -> NodeInfo:
        node_from_ft = self.get_node_from_ft(node_id)
        if node_from_ft:
            return node_from_ft
        closest_addr = self.closest_preceeding_node(node_id).onion_addr
        if closest_addr == self.onion_addr:
            return NodeInfo(self.node_id, self.onion_addr)
        successor = NodeInfo(**services.find_successor(closest_addr, self.onion_addr, node_id))
        return successor

    def in_range(self, a: int, b: int, c: int) -> bool:
        a = a % s
        b = b % s
        c = c % s
        return b in range(a, c) or b in range(c, a)

    def closest_preceeding_node(self, node_id: int) -> NodeInfo:
        ft = self.finger_table
        for i in range(len(ft)-1, 0, -1):
            if self.in_range(self.node_id, ft[i].node_id, node_id):
                return ft[i]
        return self.get_successor() # if no node in range, return the successor

    def join(self, onion_addr = bootstrap_onion):
        """Join the network"""
        try:
            if self.name == 'boot0':
                self.set_successor(NodeInfo(self.node_id, self.onion_addr))
                return 'Created the network.'
            successor = NodeInfo(**services.join(onion_addr, self.onion_addr, self.node_id))
            self.set_successor(successor)
            self.stabilize()
            print('FINGER \n{}\nPred\n{}'.format(self.finger_table, self.predecessor))
            return 'Joined the network.'
        except Exception as e:
            print("join: ", e)
            return 'Failed to join the network.'

    def stabilize(self) -> None:
        """Stabilize the network"""
        succ = self.get_successor()
        print('STABILIZE: {}'.format(succ.onion_addr))
        succ_pred = services.get_predecessor(succ.onion_addr)
        if succ_pred:
            succ_pred = NodeInfo(**succ_pred)
        print('STABILIZE PRED: {}'.format(succ_pred))
        # is the successors predecessor in between me and my successor
        if succ_pred and self.in_range(self.node_id, succ_pred.node_id, succ.node_id):
            # if so, set my successor to the successors predecessor
            self.set_successor(succ_pred)
        else:
            # otherwise notify the successor that i am its predecessor
            self.notify(self.get_successor().onion_addr)

    def notify(self, onion_addr: str) -> None:
        """Notify the node"""
        services.notify(onion_addr, self.onion_addr, self.node_id)
    
    def ack_notify(self, node: NodeInfo) -> None:
        """Acknowledge the notification"""
        pred = self.get_predecessor()
        if not pred or self.in_range(pred.node_id, node.node_id, self.node_id):
            self.predecessor = node

    def fix_fingers(self) -> None:
        """Fix the fingers"""
        self.next = self.next + 1
        if self.next >= m:
            self.next = 0
        succ_i = self.find_successor(self.node_id + 2**(self.next-1))
        self.finger_table[self.next] = succ_i

    def check_predecessor(self) -> None:
        """Check the predecessor"""
        pred = self.get_predecessor()
        if pred and not self.is_alive(pred.onion_addr):
            self.predecessor = None

    def is_alive(self, onion_addr: str) -> bool:
        """Check if the node is alive"""
        try:
            return services.ping(onion_addr) == 200
        except Exception as e:
            print(f'is_alive() Error: {e}')
            return False

    def get_msg_history(self, peer):
        try:
            msg_history = self.msg_history[peer]
            return msg_history
        except KeyError:
            return None