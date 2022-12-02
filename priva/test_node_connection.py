import sys
import time
sys.path.insert(0, '..')

from node import Node

node1 = Node("localhost", 10001, 'node-1')
node2 = Node("localhost", 10002, 'node-2')

node1.start()
node2.start()
node1.debug = True
node2.debug = True
time.sleep(1)

node1.connect_with_node("localhost", 10002)

node1.send_ping()
node2.send_ping()

nod = node1.nodes_outbound[-1]
print('\n============== \n {} \n =============='.format(nod.host))

node1.stop()
node2.stop()

node1.join()
node2.join()

print("End")