from renderer.image_helper import ImageHelper
from PIL import Image
import os
import errno

logo_name = 'teams-current-primary-light'
url = 'https://www-league.nhlstatic.com/images/logos/{}/{}.svg'
            
class LogoRenderer:
  def __init__(self, team, matrix, location):
    self.matrix = matrix
    self.location = location
    self.load(team)

  def load(self, team):
    filename = 'Assets/logos/{}/{}.png'.format(team.id, logo_name)

    try:
      self.logo = Image.open(filename)
    except FileNotFoundError:
      self.save_image(filename, team)

  def save_image(self, filename, team):
    if not os.path.exists(os.path.dirname(filename)):
      try:
        os.makedirs(os.path.dirname(filename))
      except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
          raise
          
    self.logo = ImageHelper.image_from_svg(
      url.format(logo_name, team.id)
    )
    self.logo.thumbnail((64, 32))
    #self.logo = self.logo.transpose(method=Image.FLIP_LEFT_RIGHT)
    self.logo.save(filename)

  def render(self):
    x = 0
    if self.location == 'right':
      x = self.logo.width - 21
    elif self.location == 'left':
      x = 21 - self.logo.width

    self.matrix.draw_image((x, 0), self.logo, self.location)

    