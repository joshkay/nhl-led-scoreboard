import sys
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
from renderer.matrix import Matrix
from config.main import Config

#For remote debugging only
#import ptvsd

# Allow other computers to attach to ptvsd at this IP address and port.
#ptvsd.enable_attach(address=('0.0.0.0', 3000), redirect_output=True)

# Pause the program until a remote debugger is attached
#ptvsd.wait_for_attach()

SCRIPT_NAME = "NHL-LED-SCOREBOARD"
SCRIPT_VERSION = "0.1.0"

def run():
  # Get supplied command line arguments
  commandArgs = args()

  # Check for led configuration arguments
  matrixOptions = led_matrix_options(commandArgs)
  matrixOptions.drop_privileges = False

  # Initialize the matrix
  matrix = Matrix(RGBMatrix(options = matrixOptions))

  # Print some basic info on startup
  debug.info("{} - v{} ({}x{})".format(SCRIPT_NAME, SCRIPT_VERSION, matrix.get_width(), matrix.get_height()))

  # Read scoreboard options from config.json if it exists
  scoreboard_config = ScoreboardConfig("config", commandArgs, matrix.get_width(), matrix.get_height())
  debug.set_debug_status(scoreboard_config)

  data = Data(scoreboard_config)

  config = Config()

  # Dimmer routine to automatically dim display
  dimmer = Dimmer(matrix)

  dimmerThread = threading.Thread(target=dimmer.run, args=())
  dimmerThread.daemon = True
  dimmerThread.start()
  
  # Initialize API and run on separate thread
  api = ScoreboardApi(data, dimmer, matrix, config)

  apiThread = threading.Thread(target=api.run, args=())
  apiThread.daemon = True
  apiThread.start()

  MainRenderer(matrix, data).render()

try:
   run()

except KeyboardInterrupt:
  print("Exiting NHL-LED-SCOREBOARD\n")
  sys.exit(0)
