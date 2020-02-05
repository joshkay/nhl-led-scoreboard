from flask_restful import Resource

class Brightness(Resource):
  def __init__(self, dimmer, matrix):
    self.dimmer = dimmer
    self.matrix = matrix

  def get(self):
    return { 'current_brightness': self.dimmer.brightness }

  def put(self, brightness):
    if brightness < 0:
      brightness = 0
    if brightness > 100:
      brightness = 100

    self.dimmer.brightness = brightness
    self.matrix.set_brightness(brightness)
    self.matrix.render()
    return { 'current_brightness': self.dimmer.brightness }