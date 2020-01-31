from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS
from json import dumps
from ip import get_ip
from gevent.pywsgi import WSGIServer
import logging
import debug
import os

class Team(Resource):
  def __init__(self, **kwargs):
    self.data = kwargs['data']
    self.sleepEvent = kwargs['sleepEvent']

  def get(self):
    return { 'current_team_id': self.data.get_current_team_id() }

  def put(self, id):
    self.data.set_current_team_id(id)
    self.sleepEvent.set()
    self.sleepEvent.clear()
    return { 'current_team_id': self.data.get_current_team_id() }

class Brightness(Resource):
  def __init__(self, **kwargs):
    self.dimmer = kwargs['dimmer']
    self.sleepEvent = kwargs['sleepEvent']

  def get(self):
    return { 'current_brightness': self.dimmer.brightness }

  def put(self, brightness):
    if brightness < 0:
      brightness = 0
    if brightness > 100:
      brightness = 100

    self.dimmer.brightness = brightness
    self.sleepEvent.set()
    self.sleepEvent.clear()
    return { 'current_brightness': self.dimmer.brightness }

class ScoreboardApi:
  def __init__(self, data, dimmer, sleepEvent):
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
    
    self.api.add_resource(Team, '/api/team', '/api/team/<int:id>', resource_class_kwargs={
      'data': data,
      'sleepEvent': sleepEvent
    })

    self.api.add_resource(Brightness, '/api/brightness', '/api/brightness/<int:brightness>', resource_class_kwargs={
      'dimmer': dimmer,
      'sleepEvent': sleepEvent
    })

  def run(self):
    debug.info('API running: {}'.format(get_ip()))

    self.http_server = WSGIServer(('', 80), self.app)
    self.http_server.serve_forever()
    
