from flask_restful import Resource

class Team(Resource):
  def __init__(self, data, matrix):
    self.data = data
    self.matrix = matrix

  def get(self):
    return { 'current_team_id': self.data.get_current_team_id() }

  def put(self, id):
    print(id)
    self.data.set_current_team_id(id)
    self.matrix.render()
    return { 'current_team_id': self.data.get_current_team_id() }
