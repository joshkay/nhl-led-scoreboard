from flask import Flask, request, send_from_directory, Blueprint
from flask_restful import Api
from flask_cors import CORS
from json import dumps
from api.ip import get_ip
from gevent.pywsgi import WSGIServer
import logging
import debug
import os
from api.resources.brightness import Brightness
from api.resources.team import Team
from api.resources.config import Config

class ScoreboardApi:
  def __init__(self, data, dimmer, matrix, config):
    self.app = Flask(__name__, static_folder='../client/build')
    CORS(self.app)

    # Serve React App
    @self.app.route('/', defaults={'path': ''})
    @self.app.route('/<path:path>')
    def serve(path):
      if path != "" and os.path.exists(self.app.static_folder + '/' + path):
          return send_from_directory(self.app.static_folder, path)
      else:
          return send_from_directory(self.app.static_folder, 'index.html')

    log = logging.getLogger('werkzeug')
    log.disabled = False
    self.app.logger.disabled = False

    self.api = Api(self.app)
    self.load_resources(data, dimmer, matrix, config)

  def load_resources(self, data, dimmer, matrix, config):
    root_bp = Blueprint('api', __name__)
    api_root_bp = Api(root_bp)

    api_root_bp.add_resource(Team, 
      '/team', 
      '/team/<int:id>', 
      resource_class_args={data, matrix}
    )

    api_root_bp.add_resource(Brightness, 
      '/brightness', 
      '/brightness/<int:brightness>',
      resource_class_args={dimmer, matrix}
    )

    api_root_bp.add_resource(Config, 
      '/config',
      '/config', 
      resource_class_args={config}
    )

    self.app.register_blueprint(root_bp, url_prefix='/api')

  def run(self):
    debug.info('API running: {}'.format(get_ip()))

    self.http_server = WSGIServer(('', 80), self.app)
    self.http_server.serve_forever()
    
