from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from stem.control import Controller
from flask import Flask


if __name__ == "__main__":
  app = Flask("priva")
  port = 5000
  host = "127.0.0.1"
  hidden_svc_dir = "/var/lib/tor/hidden_service"

  @app.route('/')  # type: ignore
  def index():
    return "<h1>Priva is running!</h1>"

  @app.route('/find_successor')  # type: ignore
  def find_successor():
    return "successor"
  
  print(" * Getting controller")
  controller = Controller.from_port(address="127.0.0.1", port=9151) # type: ignore
  try:
      controller.authenticate(password="")
      controller.set_options([
          ("HiddenServiceDir", hidden_svc_dir),
          ("HiddenServicePort", "80 %s:%s" % (host, str(port)))
          ])
      svc_name = open(hidden_svc_dir + "/hostname", "r").read().strip()
      print(" * Created host: %s" % svc_name)
  except Exception as e:
      print(e)
      
  app.run()
