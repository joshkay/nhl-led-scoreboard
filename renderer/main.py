from PIL import Image
import requests
import urllib3
from utils import center_text
from calendar import month_abbr
from renderer.screen_config import screenConfig
from renderer.matrix import Matrix
from renderer.fonts import Fonts
from renderer.image_helper import ImageHelper
import time
import debug
import cairosvg
from io import BytesIO

class MainRenderer:
    def __init__(self, matrix, data, dimmer, sleepEvent):
        self.matrix = Matrix(matrix, (64, 32))
        self.data = data
        self.sleepEvent = sleepEvent

        self.screen_config = screenConfig("64x32_config")
        self.width = 64
        self.height = 32

        self._dimmer = dimmer

    def render(self):
        # loop through the different state.
        while True:
            self.data.get_current_date()
            self.data.refresh_fav_team_status()
            
            self.matrix.set_brightness(self._dimmer.brightness)
            
            # Fav team game day
            if self.data.fav_team_game_today:
                debug.info('Game day State')
                self.__render_game()
            # Fav team off day
            else:
                debug.info('Off day State')
                self.__render_off_day()

    def __render_game(self):

        if self.data.fav_team_game_today == 1:
            debug.info('Scheduled State')
            self._draw_pregame()
            self.sleepEvent.wait(1800)
        elif self.data.fav_team_game_today == 2:
            debug.info('Pre-Game State')
            self._draw_pregame()
            self.sleepEvent.wait(60)
        elif (self.data.fav_team_game_today == 3) or (self.data.fav_team_game_today == 4):
            debug.info('Live State')
            # Draw the current game
            self._draw_game()
        elif (self.data.fav_team_game_today == 5) or (self.data.fav_team_game_today == 6) or (self.data.fav_team_game_today == 7):
            debug.info('Final State')
            self._draw_post_game()
            #sleep an hour
            self.sleepEvent.wait(3600)
        debug.info('ping render_game')

    def __render_off_day(self):

        debug.info('ping_day_off')
        self._draw_off_day()
        self.sleepEvent.wait(21600) #sleep 6 hours

    def _draw_pregame(self):

        if self.data.get_schedule() != 0:

            overview = self.data.schedule

            # Save when the game start
            game_time = overview['game_time']

            # Center the game time on screen.
            game_time_pos = center_text(Fonts.font_mini.getsize(game_time)[0], 32)

            # Set the position of each logo
            away_team_logo_pos = self.screen_config.team_logos_pos[str(overview['away_team_id'])]['away']
            home_team_logo_pos = self.screen_config.team_logos_pos[str(overview['home_team_id'])]['home']

            url = 'https://www-league.nhlstatic.com/images/logos/teams-current-primary-light/{}.svg'
            away_image = ImageHelper.image_from_svg(
              url.format(overview['away_team_id'])
            )
            away_image.thumbnail((64, 32))
            self.matrix.draw_image((0, 0), away_image)

            home_image = ImageHelper.image_from_svg(
              url.format(overview['home_team_id'])
            )
            home_image.thumbnail((64, 32))
            self.matrix.draw_image((32, 0), home_image)

            # Draw the text on the Data image.
            self.matrix.draw_text((22, -1), 'TODAY', font=Fonts.font_mini)
            self.matrix.draw_text(
              (game_time_pos, 5), game_time, multiline=True, 
              fill=(255, 255, 255), font=Fonts.font_mini, align="center"
            )
            self.matrix.draw_text((25, 13), 'VS', font=Fonts.font)

            # Put the data on the canvas
            self.matrix.render()
            self.matrix.clear()

            # # Put the images on the canvas
            # self.canvas.SetImage(away_team_logo.convert("RGB"), away_team_logo_pos["x"], away_team_logo_pos["y"])
            # self.canvas.SetImage(home_team_logo.convert("RGB"), home_team_logo_pos["x"], home_team_logo_pos["y"])

            # # Load the canvas on screen.
            # self.canvas = self.matrix.SwapOnVSync(self.canvas)

            # # Refresh the Data image.
            # self.image = Image.new('RGB', (self.width, self.height))
            # self.draw = ImageDraw.Draw(self.image)
        else:
            #(Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            self.sleepEvent.wait(60)  # sleep for 1 min
            # Refresh canvas
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

    def _draw_game(self):
        self.data.refresh_overview()
        overview = self.data.overview
        home_score = overview['home_score']
        away_score = overview['away_score']
        team = self.data.get_current_team_id()

        while True:

            if team != self.data.get_current_team_id():
              break

            # Refresh the data
            if self.data.needs_refresh:
                debug.info('Refresh game overview')
                self.data.refresh_overview()
                self.data.needs_refresh = False

            if self.data.overview != 0:
                overview = self.data.overview

                # Use This code if you want the goal animation to run only for your fav team's goal
                # if self.data.fav_team_id == overview['home_team_id']:
                #     if overview['home_score'] > home_score:
                #         self._draw_goal()
                # else:
                #     if overview['away_score'] > away_score:
                #         self._draw_goal()

                # Use this code if you want the goal animation to run for both team's goal.
                # Run the goal animation if there is a goal.
                if self.data.home_team_goal or self.data.away_team_goal:
                   self._draw_goal()

                # Prepare the data
                score = '{}-{}'.format(overview['away_score'], overview['home_score'])
                period = overview['period']
                time_period = overview['time']

                # Set the position of the information on screen.
                time_period_pos = center_text(Fonts.font_mini.getsize(time_period)[0], 32)
                score_position = center_text(Fonts.font.getsize(score)[0], 32)
                period_position = center_text(Fonts.font_mini.getsize(period)[0], 32)

                # Set the position of each logo on screen.
                away_team_logo_pos = self.screen_config.team_logos_pos[str(overview['away_team_id'])]['away']
                home_team_logo_pos = self.screen_config.team_logos_pos[str(overview['home_team_id'])]['home']

                # Open the logo image file
                away_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[overview['away_team_id']]['abbreviation']))
                home_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[overview['home_team_id']]['abbreviation']))

                # Draw the text on the Data image.
                self.draw.multiline_text((score_position, 15), score, fill=(255, 255, 255), font=Fonts.font, align="center")
                self.draw.multiline_text((period_position, -1), period, fill=(255, 255, 255), font=Fonts.font_mini, align="center")
                self.draw.multiline_text((time_period_pos, 5), time_period, fill=(255, 255, 255), font=Fonts.font_mini, align="center")

                # Put the data on the canvas
                self.canvas.SetImage(self.image.convert('RGB'), 0, 0)

                # Put the images on the canvas
                self.canvas.SetImage(away_team_logo.convert("RGB"), away_team_logo_pos["x"], away_team_logo_pos["y"])
                self.canvas.SetImage(home_team_logo.convert("RGB"), home_team_logo_pos["x"], home_team_logo_pos["y"])

                # Load the canvas on screen.
                self.canvas = self.matrix.SwapOnVSync(self.canvas)

                # Refresh the Data image.
                self.image = Image.new('RGB', (self.width, self.height))
                self.draw = ImageDraw.Draw(self.image)

                # Check if the game is over
                if overview['game_status'] == 6 or overview['game_status'] == 7:
                    debug.info('GAME OVER')
                    break

                self.data.needs_refresh = True
                self.sleepEvent.wait(15)
            else:
                # (Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
                self.draw.line((0, 0) + (self.width, 0), fill=128)
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                self.sleepEvent.wait(60)  # sleep for 1 min

    def _draw_post_game(self):
        self.data.refresh_overview()
        if self.data.overview != 0:
            overview = self.data.overview

            # Prepare the data
            game_date = '{} {}'.format(month_abbr[self.data.month], self.data.day)
            score = '{}-{}'.format(overview['away_score'], overview['home_score'])
            period = overview['period']
            time_period = overview['time']

            # Set the position of the information on screen.
            game_date_pos = center_text(Fonts.font_mini.getsize(game_date)[0], 32)
            time_period_pos = center_text(Fonts.font_mini.getsize(time_period)[0], 32)
            score_position = center_text(Fonts.font.getsize(score)[0], 32)

            # Draw the text on the Data image.
            self.draw.multiline_text((game_date_pos, -1), game_date, fill=(255, 255, 255), font=Fonts.font_mini, align="center")
            self.draw.multiline_text((score_position, 15), score, fill=(255, 255, 255), font=Fonts.font, align="center")
            self.draw.multiline_text((time_period_pos, 5), time_period, fill=(255, 255, 255), font=Fonts.font_mini, align="center")

            # Only show the period if the game ended in Overtime "OT" or Shootouts "SO"
            if period == "OT" or period == "SO":
                period_position = center_text(Fonts.font_mini.getsize(period)[0], 32)
                self.draw.multiline_text((period_position, 11), period, fill=(255, 255, 255), font=Fonts.font_mini,align="center")

            # Open the logo image file
            away_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[overview['away_team_id']]['abbreviation']))
            home_team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[overview['home_team_id']]['abbreviation']))

            # Set the position of each logo on screen.
            away_team_logo_pos = self.screen_config.team_logos_pos[str(overview['away_team_id'])]['away']
            home_team_logo_pos = self.screen_config.team_logos_pos[str(overview['home_team_id'])]['home']

            # Put the data on the canvas
            self.canvas.SetImage(self.image.convert('RGB'), 0, 0)

            # Put the images on the canvas
            self.canvas.SetImage(away_team_logo.convert("RGB"), away_team_logo_pos["x"], away_team_logo_pos["y"])
            self.canvas.SetImage(home_team_logo.convert("RGB"), home_team_logo_pos["x"], home_team_logo_pos["y"])

            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)

            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

        else:
            # (Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            self.sleepEvent.wait(60)  # sleep for 1 min

    def _draw_goal(self):

        debug.info('SCOOOOOOOORE, MAY DAY, MAY DAY, MAY DAY, MAY DAAAAAAAAY - Rick Jeanneret')
        # Load the gif file
        im = Image.open("Assets/goal_light_animation.gif")
        # Set the frame index to 0
        frameNo = 0

        self.canvas.Clear()

        # Go through the frames
        x = 0
        while x is not 5:
            try:
                im.seek(frameNo)
            except EOFError:
                x += 1
                frameNo = 0
                im.seek(frameNo)

            self.canvas.SetImage(im.convert('RGB'), 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            frameNo += 1
            self.sleepEvent.wait(0.1)

    def _draw_off_day(self):
        self.data.get_lastgame()
        overview = self.data.lastgame
        print("Debug data: Render")
        print(overview)
        home_score = overview['home_score']
        away_score = overview['away_score']

        if self.data.get_current_team_id() == overview['home_team_id']:
          score = '{}-{}'.format(overview['home_score'], overview['away_score'])
        else:
          score = '{}-{}'.format(overview['away_score'], overview['home_score'])

        # Open Fav Team Logo
        team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[self.data.get_current_team_id()]['abbreviation']))

        # Set Text
        self.draw.text((1, -1), 'No Game Today', font=Fonts.font_mini,  align="center")
        #self.draw.text((1, 5), 'Today', font=Fonts.font_mini,  align="center")

        try:
          self.image.paste(team_logo, (32, 0), team_logo)
        except:
          self.image.paste(team_logo, (32, 0))

        # Set Last Game Day
        self.draw.text((8, 13), overview['game_date'], font=Fonts.font_mini,  align="center")

        # Set Last Score
        self.draw.multiline_text((9, 19), score, fill=(255, 255, 255), font=Fonts.font, align="center")

        # Win/Loss?
        if home_score > away_score:
          if self.data.get_current_team_id() == overview['home_team_id']:
            winloss = "W"
          else:
            winloss = "L"
        else:
          if self.data.get_current_team_id() == overview['home_team_id']:
            winloss = "L"
          else:
            winloss = "W"

        if winloss == "W":
          wlfill = (0, 225, 0)
        else:
          wlfill = (255, 0, 0)

        # Set Win/Loss
        self.draw.multiline_text((1, 15), winloss, fill=wlfill, font=Fonts.font, align="center")
        
        self.canvas.SetImage(self.image.convert('RGB'), 0, 0)
 
        # Refresh canvas
        self.canvas = self.matrix.SwapOnVSync(self.canvas)
        self.image = Image.new('RGBA', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
  
    def draw_face(self):
      url = "https://nhl.bamcontent.com/images/headshots/current/168x168/8478403.jpg"
      img = Image.open(requests.get(url, stream=True).raw).convert('RGBA')

      img = img.crop((img.size[0] * 0.35, img.size[1] * 0.3, img.size[0] - (img.size[0] * 0.4), img.size[0] - (img.size[0] * 0.4)))
      img.thumbnail((64, 32))

      self.image.paste(img, (0, 0), img)

      self.canvas.SetImage(self.image.convert('RGB'), 0, 0)
 
      # Refresh canvas
      self.canvas = self.matrix.SwapOnVSync(self.canvas)
      self.image = Image.new('RGBA', (self.width, self.height))
      self.draw = ImageDraw.Draw(self.image)

    def draw_logo(self):
      #url = "https://nhl.bamcontent.com/images/headshots/current/168x168/8478403.jpg"
      url = 'https://www-league.nhlstatic.com/images/logos/teams-current-primary-light/10.svg'
      #img = Image.open(requests.get(url, stream=True).raw).convert('RGBA')

      out = BytesIO()
      cairosvg.svg2png(url=url, write_to=out)
      img = Image.open(out)
      img = img.crop(img.getbbox())

      img.thumbnail((64, 32))

      self.draw.text((0, 0), 'TEXT ON BOTTOM', font=Fonts.font_mini,  align="center")

      self.image.paste(img, (0, 0), img)

      team_logo = Image.open('logos/{}.png'.format(self.data.get_teams_info[self.data.get_current_team_id()]['abbreviation']))
      
      self.image.paste(team_logo, (32, 0), team_logo)

      self.draw.text((0, 25), 'TEXT ON TOP', font=Fonts.font_mini,  align="center")

      self.canvas.SetImage(self.image.convert('RGB'), 0, 0)
      
      # Refresh canvas
      self.canvas = self.matrix.SwapOnVSync(self.canvas)
      self.image = Image.new('RGBA', (self.width, self.height))
      self.draw = ImageDraw.Draw(self.image)