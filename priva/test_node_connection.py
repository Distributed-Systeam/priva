import sys
import time
sys.path.insert(0, '..')

from chord_node import ChordNode

node1 = ChordNode("localhost", 10001, 'node-1')
node2 = ChordNode("localhost", 10002, 'node-2')

node1.start()
node2.start()
node1.debug = True
node2.debug = True
time.sleep(1)
print("\n\n>>>>>>>>>> ", node1.node_id, " <<<<<<<<<<\n\n")
node1.connect_with_node("localhost", 10002)

nod1 = node1.nodes_outbound[-1]
nod2 = node2.nodes_inbound[-1]
print('\n============== \n {} \n =============='.format(nod1.host))
node1.send_to_node(nod1, "Hello from node 1")
node2.send_to_node(nod2, "Hello from node 2")

node1.node_message(nod1, "Hello from node 1")
node1.print_connections()

node1.stop()
node2.stop()

print("End")