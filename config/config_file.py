import json

class ConfigFile:
  def __init__(self, path):
    self.path = path
    self.load()

  def load(self):
    with open(self.path) as f:
      self.json = json.load(f)

def save(self):
    with open(self.path, 'w') as f:
      json.dump(self.json, f)