# Priva (Distributed Systems course project)

Distributed P2P chat application in P2P network.

# Planning quick view

- No centralized server (P2P network)

- Open network, anyone can join

- States:
	- Number of neighbor nodes (messaging connection)
	- Chat history

- Distributed hash table to keep node information (Chord). 
	- Keep track of nodes in network by pulling neighbor node information
	- Server nodes included in network (3 in total, distributed evenly according to Chord 'circle').
		- Works same way as any other node in the network, expect:
			- No direct messaging
			- Gateway to the P2P network
			- Creates hash for new nodes joining the network
			- Responsibe of initializing the new node addition to the network
			- Can not be removed from the network
			
- Hash created from **name** + **6 character random string (id)**.
	- Id is alphanumerical (a-Z, 0-9)

- Establish P2P message connection using DHT

## Architecture

![Architecture pic](https://github.com/Distributed-Systeam/priva/blob/documentations/planning/P2P%20network%20architecture.pdf?raw=true)
	

## Code implementation plan

- Language: python (javascript)

- Libary to impelemnt network
	- python-p2p-network (https://github.com/macsnoeren/python-p2p-network)
	
## Not compatible anymore

- States:
	- Consensus on threshold value
	
- Network can change (neighbor nodes)
	- Direct messaging creates new neighbor if not already
	
- Threshold value for amount of neighbor nodes

## Development

Spin up a python virtual environment

```bash
# install venv python module
> sudo apt install python3.8-venv
# create the virtual environment
> python3 -m venv venv
# initiate the vitual environment
> source venv/bin/activate
```
