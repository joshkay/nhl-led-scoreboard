from datetime import datetime, timedelta
from data.scoreboard_config import ScoreboardConfig
from renderer.main import MainRenderer
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils import args, led_matrix_options
from data.data import Data
import debug
from api.main import ScoreboardApi
import threading
import sys

SCRIPT_NAME = "NHL Scoreboard"
SCRIPT_VERSION = "0.1.0"

def run():
  # Get supplied command line arguments
  commandArgs = args()

  # Check for led configuration arguments
  matrixOptions = led_matrix_options(commandArgs)

  # Initialize the matrix
  matrix = RGBMatrix(options = matrixOptions)

  # Print some basic info on startup
  debug.info("{} - v{} ({}x{})".format(SCRIPT_NAME, SCRIPT_VERSION, matrix.width, matrix.height))

  # Read scoreboard options from config.json if it exists
  config = ScoreboardConfig("config", commandArgs)
  debug.set_debug_status(config)

  data = Data(config)

  # Event used to sleep when rendering
  # Allows API to cancel the sleep
  sleepEvent = threading.Event()

  # Initialize API and run on separate thread
  api = ScoreboardApi(data, sleepEvent)
  
  apiThread = threading.Thread(target=api.run, args=())
  apiThread.daemon = True
  apiThread.start()

  MainRenderer(matrix, data, sleepEvent).render()

try:
  run()
except KeyboardInterrupt:
  debug.info('Goodbye! :)')
  sys.exit(0)