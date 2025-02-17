from PIL import Image, ImageDraw
from rgbmatrix import graphics

class Matrix:
  def __init__(self, matrix, size):
    self.matrix = matrix
    self.brightness = None
    self.width = size[0]
    self.height = size[1]

    # Create a new data image.
    self.image = Image.new('RGBA', (self.width, self.height))
    self.draw = ImageDraw.Draw(self.image)

    # Create a new data image.
    self.image = Image.new('RGBA', (self.width, self.height))
    self.draw = ImageDraw.Draw(self.image)
    
    self.canvas = matrix.CreateFrameCanvas()

  def set_brightness(self, brightness):
    self.brightness = brightness
    self.matrix.brightness = self.brightness

  def draw_text(self, position, text, font, fill=None, align="left", multiline=False):
    if (multiline):
      self.draw.multiline_text(position, text, fill=fill, font=font, align=align)
    else:
      self.draw.text(position, text, fill=fill, font=font)

  def draw_image(self, position, image):
    self.image.paste(image, position, image)

  def render(self):
    self.canvas.SetImage(self.image.convert('RGB'), 0, 0)
    self.canvas = self.matrix.SwapOnVSync(self.canvas)

  def clear(self):
    self.image.paste(0, (0, 0, self.get_width(), self.get_height()))

  def get_width(self):
    return self.width
  
  def get_height(self):
    return self.height

  