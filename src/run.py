import os
import json
import shutil
from stem.control import Controller
from flask import Flask, request
from priva_modules import ui, chord_node
from threading import Thread
from colorama import Fore, Style
from time import sleep
import logging

onion_addr = None
priva_node = None
cntrl = None
hidden_service_dir = None

app = Flask(__name__)

@app.route('/')
def index():
  return "<h1>Priva is running on port 80!</h1>"

@app.route('/get_predecessor', methods=['GET'])
def get_predecessor():
  pred_id = 'test_predecessor_id'
  return "<h1>Predecessor found! {}</h1>".format(pred_id)

@app.route('/find_successor', methods = ['GET'])
def find_successor():
  succ_id = request.args.get('succ_node_id')
  return "<h1>Successor found! {}</h1>".format(succ_id)

@app.route('/join', methods=['POST'])
def join():
  node_id = request.json['node_id']
  successor = priva_node.find_successor(node_id)
  return json.dumps(successor)

@app.route('/notify', methods=['POST'])
def notify():
  return "<h1>I am notified!</h1>"

@app.route('/ping', methods=['GET'])
def ping():
  return "<h1>I have been pinged!</h1>"

def start_server():
  with Controller.from_port() as controller:
    global cntrl
    cntrl = controller
    controller.authenticate()

    print(' * Connecting to tor...')
    # All hidden services have a directory on disk. Lets put ours in tor's data
    # directory.

    global hidden_service_dir
    hidden_service_dir = os.path.join(controller.get_conf('DataDirectory', '/tmp'), 'priva')

    # THIS RESETS THE TOR CONFIGURATION
    #if os.path.isdir(hidden_service_dir):
    #  controller.remove_hidden_service(hidden_service_dir)
    #  shutil.rmtree(hidden_service_dir)

    #print(" * Creating our hidden service in %s" % hidden_service_dir)
    try:
      global onion_addr
      global priva_node
      if not os.path.isdir(hidden_service_dir):
        # Create a hidden service where visitors of port 80 get redirected to local
        # port 5000 (this is where Flask runs by default).
        result = controller.create_hidden_service(hidden_service_dir, 80, target_port = 5000)
        f = open('.onion.txt', 'w')
        f.write(f'{result.hostname}')
        f.close()
    except:
      print(f"{Fore.RED}* Error: cannot start tor hidden service!{Style.RESET_ALL}")
      
    # The hostname is only available when we can read the hidden service
    # directory. This requires us to be running with the same user as tor.
    try:
      f = open('.onion.txt', 'r')
      onion = f.readline()
      print(onion)
      onion_addr = onion
      priva_node = chord_node.ChordNode(onion_addr)
      #print(" * Priva is available at %s, press ctrl+c to quit" % result.hostname)
    except Exception as e:
      print(f"{Fore.RED} * Unable to determine our service's hostname: {e}{Style.RESET_ALL}")

    try:
      log = logging.getLogger('werkzeug')
      log.setLevel(logging.ERROR)
      app.run()
    finally:
      # Shut down the hidden service and clean it off disk. Note that you *don't*
      # want to delete the hidden service directory if you'd like to have this
      # same *.onion address in the future.
      print(" * Shutting down our hidden service")
      controller.remove_hidden_service(hidden_service_dir)
      shutil.rmtree(hidden_service_dir)

    app.run()

# run the server in the background
t = Thread(target=start_server)
t.start()
#e = threading.Event()
sleep(1)
if onion_addr:
  print(f" * Tor hidden service running at {onion_addr}")
status = ui.UI.init_ui(priva_node)
if status == 'exited':
  print(" * Shutting down the hidden service\n")
  os._exit(0)
  