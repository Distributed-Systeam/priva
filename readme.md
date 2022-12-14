# Priva

Decentralised P2P chat application.

## Development

Clone the repository

```bash
$ git clone https://github.com/Distributed-Systeam/priva.git
$ cd priva/
```

Spin up a python virtual environment

```bash
# install venv python module
$ sudo apt install python3.8-venv
# create the virtual environment
$ python3 -m venv venv
# initiate the virtual environment
$ source venv/bin/activate
# install the requirements
$ pip install -r requirements.txt
```

`Note!` Priva runs over tor. You must have [Tor browser](https://www.torproject.org/download) running in the background to use the application.

The first node in the network must be named boot0. It serves as a bootstrap node for other nodes connecting to the network. The onion address of the bootstrap node is hard coded at the beginning of src/priva_modules/chord_node.py file. This address must correspond to the address printed out as the boot0 node is started.

## Usage

```bash
# run the application
$ python3 src/run.py
```

![username-selection](https://github.com/Distributed-Systeam/priva/blob/main/img/username-selection-1.png)

![network-created](https://github.com/Distributed-Systeam/priva/blob/main/img/username-selection-2.png)

![usage](https://github.com/Distributed-Systeam/priva/blob/main/img/usage.png)