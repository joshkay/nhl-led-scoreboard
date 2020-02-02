from PIL import Image, ImageDraw
from rgbmatrix import graphics

class Matrix:
  def __init__(self, matrix):
    self.matrix = matrix
    self.brightness = None

    # Create a new data image.
    self.image = Image.new('RGBA', (self.get_width(), self.get_height()))
    self.draw = ImageDraw.Draw(self.image)

    self.pixels = self.image.load()
    
    self.canvas = matrix.CreateFrameCanvas()

  def set_brightness(self, brightness):
    self.brightness = brightness
    self.matrix.brightness = self.brightness

  def draw_text(self, position, text, font, fill=None, align="left", multiline=False):
    if (multiline):
      self.draw.multiline_text(position, text, fill=fill, font=font, align=align)
    else:
      self.draw.text(position, text, fill=fill, font=font)

  def draw_image(self, position, image, location="left"):
    x, y = position

    if (location == "right"):
      x += self.get_width() - image.size[0]

    self.image.paste(image, (x, y), image)

  def set_pixel(self, position, color):
    self.pixels = self.image.load()
    self.pixels[position] = color

  def render(self):
    self.canvas.SetImage(self.image.convert('RGB'), 0, 0)
    self.canvas = self.matrix.SwapOnVSync(self.canvas)

  def clear(self):
    self.image.paste(0, (0, 0, self.get_width(), self.get_height()))

  def get_width(self):
    return self.matrix.width
  
  def get_height(self):
    return self.matrix.height

  