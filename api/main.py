from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from ip import get_ip
from gevent.pywsgi import WSGIServer
import logging
import debug

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


class ScoreboardApi:
  def __init__(self, data, sleepEvent):
    self.app = Flask(__name__)

    log = logging.getLogger('werkzeug')
    log.disabled = True
    self.app.logger.disabled = True

    self.api = Api(self.app)
    
    self.api.add_resource(Team, '/team', '/team/<int:id>', resource_class_kwargs={
      'data': data,
      'sleepEvent': sleepEvent
    })

  def run(self):
    debug.info('API running: {}'.format(get_ip()))

    http_server = WSGIServer(('', 5000), self.app)
    http_server.serve_forever()
    
