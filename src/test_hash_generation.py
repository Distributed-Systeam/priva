from chord_node import ChordNode

node1 = ChordNode("localhost", 10001, 'node-1')
node2 = ChordNode("localhost", 10002, 'node-2')
node3 = ChordNode("localhost", 10003, 'node-3')

print("node1 node_id: ", node1.node_id)
print("node2 node_id: ", node2.node_id)
print("node3 node_id: ", node3.node_id)

print("node1 user_id: ", node1.user_id)
print("node2 user_id: ", node2.user_id)
print("node3 user_id: ", node3.user_id)

node1.join()
node2.join()
node3.join()

print("node1 finger_table: ", node1.finger_table)
print("node2 finger_table: ", node2.finger_table)
print("node3 finger_table: ", node3.finger_table)

print(node1.in_range(node1.node_id, node2.node_id, node3.node_id))