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
from dimmer import Dimmer
from apscheduler.schedulers.background import BackgroundScheduler

#For remote debugging only
#import ptvsd

# Allow other computers to attach to ptvsd at this IP address and port.
#ptvsd.enable_attach(address=('0.0.0.0', 3000), redirect_output=True)

# Pause the program until a remote debugger is attached
#ptvsd.wait_for_attach()


SCRIPT_NAME = "NHL Scoreboard"
SCRIPT_VERSION = "0.1.4"

def run():
  # Get supplied command line arguments
  commandArgs = args()

  # Check for led configuration arguments
  matrixOptions = led_matrix_options(commandArgs)
  matrixOptions.drop_privileges = False

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

  # Dimmer routine to automatically dim display
  scheduler = BackgroundScheduler()
  dimmer = Dimmer(scheduler, sleepEvent)

  scheduler.start()
  
  # Initialize API and run on separate thread
  api = ScoreboardApi(data, dimmer, sleepEvent)
  
  apiThread = threading.Thread(target=api.run, args=())
  apiThread.daemon = True
  apiThread.start()

  MainRenderer(matrix, data, dimmer, sleepEvent).render()

try:
  run()
except KeyboardInterrupt:
  debug.info('Goodbye! :)')
  sys.exit(0)
