from flask_restful import Resource
from flask import jsonify

class Config(Resource):
  def __init__(self, config):
    self.config = config

  def get(self):
    return jsonify(self.config.settings.json)

  def put(self, id):
    print(id)
    self.data.set_current_team_id(id)
    self.matrix.render()
    return { 'current_team_id': self.data.get_current_team_id() }
