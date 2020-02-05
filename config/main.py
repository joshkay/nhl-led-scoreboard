import json
from config.config_file import ConfigFile

class Config:
  def __init__(self):
    self.settings = ConfigFile('config/settings.json')
      