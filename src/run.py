import os
import json
from stem.control import Controller
from flask import Flask, request
from priva_modules import ui, chord_node
from threading import Thread
from colorama import Fore, Style
from time import sleep
import logging
import json

service = None
service_running = False
priva_node = None
cntrl = None
key_path = os.path.expanduser('.private_key')

app = Flask(__name__)

@app.route('/')
def index():
  return "<h1>Priva is running on port 80!</h1>"

@app.route('/get_predecessor', methods=['GET'])
def get_predecessor():
  pred = priva_node.get_predecessor()
  if pred:
    return json.dumps(pred.__dict__)
  return json.dumps(None)

@app.route('/find_successor', methods=['POST'])
def find_successor():
  node_id = request.json['node_id']
  successor = priva_node.find_successor(node_id).__dict__
  return json.dumps(successor)

@app.route('/join', methods=['POST'])
def join():
  node = chord_node.NodeInfo(**request.json)
  successor = priva_node.find_successor(node.node_id).__dict__
  if (successor['node_id'] == priva_node.node_id):
    priva_node.set_successor(node)
  return json.dumps(successor)

@app.route('/notify', methods=['POST'])
def notify():
  node_info = chord_node.NodeInfo(**request.json)
  priva_node.ack_notify(node_info)
  return 'Im notified'

@app.route('/ping', methods=['GET'])
def ping():
  return "<h1>I have been pinged!</h1>"

@app.route('/connect', methods=['POST'])
def connect():
  data = request.json
  contact_info = chord_node.ContactInfo(**data)
  priva_node.current_msg_peer = contact_info
  return json.dumps({"user_id": priva_node.user_id, 'onion_addr': priva_node.onion_addr})

@app.route('/message', methods=['POST'])
def message():
  data = request.get_json()
  # todo: add message to msg_history
  msg = data['msg']
  priva_node.last_message = msg
  msg_from = data['user_id']
  msg_history = priva_node.get_msg_history(msg_from)
  if msg_history == None:
    priva_node.msg_history[msg_from] = [f'{msg_from}: {msg}']
  else:
    priva_node.msg_history[msg_from].append(f'{msg_from}: {msg}')
  if priva_node.current_msg_peer.user_id == msg_from:
    print(f'{Fore.BLUE}{msg_from}{Style.RESET_ALL}: {msg}')
  return 'message received'

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
      if not os.path.exists(key_path):
        service = controller.create_ephemeral_hidden_service({80: 5000}, await_publication = True)
        print(f' * Started a new tor hidden service at {service.service_id}.onion')
        service_running = True

        with open(key_path, 'w') as key_file:
          key_file.write('%s:%s' % (service.private_key_type, service.private_key))
      else:
        with open(key_path) as key_file:
          key_type, key_content = key_file.read().split(':', 1)

        service = controller.create_ephemeral_hidden_service({80: 5000}, key_type = key_type, key_content = key_content, await_publication = True)
      priva_node = chord_node.ChordNode(service.service_id)
      print(f' * Resumed tor hidden service at {service.service_id}.onion')
      service_running = True
    except Exception as e:
      print(f"{Fore.RED}* Could not start tor hidden service: {e}{Style.RESET_ALL}")
    
    try:
      log = logging.getLogger('werkzeug')
      log.setLevel(logging.ERROR)
      app.run()
    finally:
      print(" * Shutting down the hidden service")

    app.run()

# run the server in the background
t = Thread(target=start_server)
t.start()
# wait for the hidden service
while True:
  if service_running == True:
    # give time to print out flask stuff
    sleep(1)
    break
status = ui.UI.init_ui(priva_node)
if status == 'exited':
  print(" * Shutting down the hidden service\n")
  os._exit(0)
  