from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
import debug

class Team(Resource):
  def __init__(self, **kwargs):
    self.data = kwargs['data']

  def get(self):
    return { 'fav_team_id': self.data.get_fav_team_id() }

  def put(self, id):
    self.data.set_fav_team_id(id)
    return { 'fav_team_id': self.data.get_fav_team_id() }


class ScoreboardApi:
  def __init__(self, data):
    self.app = Flask(__name__)
    self.app.debug = False

    self.api = Api(self.app)
    
    self.api.add_resource(Team, '/team', '/team/<int:id>', resource_class_kwargs={'data': data})

  def run(self):
    debug.info('hi')
    self.app.run(host='0.0.0.0')
