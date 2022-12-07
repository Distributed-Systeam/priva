import sys
import time
sys.path.insert(0, '..')

from messaging_node import MessagingNode
from bootstrap_node import BootstrapNode

b_node1 = BootstrapNode(ip_addr="localhost", port=10001, name='bootstrap-1')

id = b_node1.ack_join('localhost', 10002, 'm_node-1')
print(id)
