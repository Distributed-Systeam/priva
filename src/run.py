import os
import shutil
from stem.control import Controller
from flask import Flask
from priva_modules import ui
from threading import Thread
from colorama import Fore, Style
from time import sleep
import logging

app = Flask(__name__)

@app.route('/')
def index():
  return "<h1>Priva is running on port 80!</h1>"

@app.route('/find_successor')
def find_successor():
  return "<h1>Successor found!</h1>"

onion_addr = None
controller = None
hidden_service_dir = None
def start_server():
  global controller
  try:
    with Controller.from_port() as controller:
      controller.authenticate()

      print(' * Connecting to tor...')
      # All hidden services have a directory on disk. Lets put ours in tor's data
      # directory.
      global hidden_service_dir
      hidden_service_dir = os.path.join(controller.get_conf('DataDirectory', '/tmp'), 'priva')

      if os.path.isdir(hidden_service_dir):
        controller.remove_hidden_service(hidden_service_dir)
        shutil.rmtree(hidden_service_dir)

      # Create a hidden service where visitors of port 80 get redirected to local
      # port 5000 (this is where Flask runs by default).

      #print(" * Creating our hidden service in %s" % hidden_service_dir)
      try:
        global onion_addr
        result = controller.create_hidden_service(hidden_service_dir, 80, target_port = 5000)
      except:
        print(f'{Fore.RED}* Error: cannot start tor hidden service!{Style.RESET_ALL}')
      # The hostname is only available when we can read the hidden service
      # directory. This requires us to be running with the same user as tor.

      if result.hostname:
        onion_addr = result.hostname
        #print(" * Priva is available at %s, press ctrl+c to quit" % result.hostname)
      else:
        print(" * Unable to determine hidden service's hostname, probably due to being unable to read the hidden service directory")

      try:
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        app.run()
      finally:
        # Shut down the hidden service and clean it off disk. Note that you *don't*
        # want to delete the hidden service directory if you'd like to have this
        # same *.onion address in the future.
        print(" * Shutting down the hidden service")
        controller.remove_hidden_service(hidden_service_dir)
        shutil.rmtree(hidden_service_dir)

      app.run()
  except:
    print('Error: Tor service could not be started. Is Tor browser not running?')

# run the server in the background
t = Thread(target=start_server)
t.start()
sleep(1)
if onion_addr:
  print(f" * Tor hidden service running at {onion_addr}")
  status = ui.UI.init_ui(onion_addr)
  if status == 'exited':
    print(" * Shutting down the hidden service")
    controller.remove_hidden_service(hidden_service_dir)
    shutil.rmtree(hidden_service_dir)
    print(f'\n{Fore.YELLOW}Press Ctrl + c to quit...')
