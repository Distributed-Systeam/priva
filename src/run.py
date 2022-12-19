#########
# run.py - entrypoint for the priva app
# Tor browser must be running in the background
#########
import os
import json
from typing import Optional
from stem.control import Controller
from flask import Flask, request
from priva_modules import ui, chord_node
from threading import Thread
from colorama import Fore, Style
from time import sleep
import logging
import json

# global variables used in two threads
service = None
service_running = False
priva_node = None
priva_node: Optional[chord_node.ChordNode] = None
cntrl = None

key_path = os.path.expanduser('.private_key')

app = Flask(__name__)

##################
# Server routes
##################

# base route to see if the tor hidden service is reachable
@app.route('/')
def index():
  return "<h1>Priva is running on port 80!</h1>"

# return the current predecessor
@app.route('/get_predecessor', methods=['GET'])
def get_predecessor():
  pred = priva_node.get_predecessor()
  if pred:
    return json.dumps(pred.__dict__)
  return json.dumps(None)

# find the successor of the node given as a request parameter
@app.route('/find_successor', methods=['POST'])
def find_successor():
  data = request.json
  if data == None:
    return 'No node info provided'
  node_id = data['node_id']
  successor = priva_node.find_successor(node_id).__dict__
  return json.dumps(successor)

# give the requester node details where to insert itself in the chord ring 
@app.route('/join', methods=['POST'])
def join():
  data = request.json
  if data == None:
    return 'No node info provided'
  node = chord_node.NodeInfo(**data)
  successor = priva_node.find_successor(node.node_id).__dict__
  if (successor['node_id'] == priva_node.node_id):
    priva_node.set_successor(node)
  return json.dumps(successor)

# called when the node might have a wrong predecessor
# helps the chord ring stay healthy 
@app.route('/notify', methods=['POST'])
def notify():
  data = request.json
  if data == None:
    return 'No node info provided'
  node_info = chord_node.NodeInfo(**data)
  priva_node.ack_notify(node_info)
  return 'Im notified'

# helps to figure out if the node is alive
@app.route('/ping', methods=['GET'])
def ping():
  return "<h1>I have been pinged!</h1>"

# listen for connect attempts from other peers
@app.route('/connect', methods=['POST'])
def connect():
  data = request.json
  if data == None:
    return 'No contact info provided'
  contact_info = chord_node.ContactInfo(**data)
  print('Getting a connect attempt from: {}'.format(contact_info.user_id))
  return json.dumps({"user_id": priva_node.user_id, 'onion_addr': priva_node.onion_addr})

# listen for messages sent by other peers
@app.route('/message', methods=['POST'])
def message():
  data = request.json
  if data == None:
    return 'No message provided'
  priva_node.receive_msg(data["user_id"], data["msg"])
  return 'message received'

# return the current ancestor
@app.route('/get_ancestor', methods=['GET'])
def get_ancestor():
  successor = priva_node.get_successor()
  if successor:
    return json.dumps(successor.__dict__)
  return json.dumps(None)

# start the tor hidden service
def start_server():
  with Controller.from_port() as controller:
    global cntrl
    cntrl = controller
    controller.authenticate()

    print(' * Connecting to tor...')
    try:
      global service
      global service_running
      global priva_node
      # check if there is an existing private key for the tor hidden service
      # the private key determines the onion address of the hidden service
      # if no key is found, create one
      if not os.path.exists(key_path):
        service = controller.create_ephemeral_hidden_service({80: 5000}, await_publication = True)
        print(f' * Started a new tor hidden service at {service.service_id}.onion')
        service_running = True

        with open(key_path, 'w') as key_file:
          key_file.write('%s:%s' % (service.private_key_type, service.private_key))
      # use the existing private key for the hidden service
      else:
        with open(key_path) as key_file:
          key_type, key_content = key_file.read().split(':', 1)

        service = controller.create_ephemeral_hidden_service({80: 5000}, key_type = key_type, key_content = key_content, await_publication = True)
        print(f' * Resumed tor hidden service at {service.service_id}.onion')
      priva_node = chord_node.ChordNode(f'{service.service_id}.onion')
      service_running = True # flag indicating that the UI can be started
    except Exception as e:
      print(f"{Fore.RED}* Could not start tor hidden service: {e}{Style.RESET_ALL}")
    
    try:
      log = logging.getLogger('werkzeug')
      log.setLevel(logging.ERROR)
      app.run()
    finally:
      print(" * Shutting down the hidden service")

    app.run()

# run the server (tor hidden service) and the UI in different threads
t = Thread(target=start_server)
t.start()
# wait for the hidden service to start the UI
while True:
  if service_running == True:
    # give time to print out flask stuff
    sleep(1)
    break
ui = ui.UI(priva_node)
# start the UI
status = ui.init_ui()
if status == 'exited':
  print(" * Shutting down the hidden service\n")
  os._exit(0)
  