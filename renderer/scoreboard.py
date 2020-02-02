from PIL import Image, ImageFont, ImageDraw, ImageSequence
from utils import center_text, convert_date_format
from renderer.logo import LogoRenderer
from renderer.matrix import Matrix

class ScoreboardRenderer:
    def __init__(self, data, matrix, scoreboard, index):
        self.data = data
        self.status = data.status
        self.layout = self.data.config.layout
        self.font = self.layout.font
        self.font_large = self.layout.font_large
        self.scoreboard = scoreboard
        self.index = index

        self.matrix = matrix

        self.away_logo = LogoRenderer(self.scoreboard.away_team, self.matrix, "left")
        self.home_logo = LogoRenderer(self.scoreboard.home_team, self.matrix, "right")

    def render(self):
        # Create a new data image.
        self.matrix.clear()
        
        self.away_logo.render()
        self.home_logo.render()

        if self.status.is_scheduled(self.scoreboard.status):
            self.draw_scheduled()

        if self.status.is_live(self.scoreboard.status):
            self.draw_live()

        if self.status.is_final(self.scoreboard.status):
            self.draw_final()

        if self.status.is_irregular(self.scoreboard.status):
            pass


    def draw_scheduled(self):
        start_time = self.scoreboard.start_time

        # Center the game time on screen.
        game_time_pos = center_text(self.font.getsize(start_time)[0], 32)

        # Draw the text on the Data image.
        """ TODO: need to use center_text function for all text"""
        self.matrix.draw_text((22, -1), 'TODAY', font=self.layout.font)
        self.matrix.draw_text((game_time_pos, 5), start_time, fill=(255, 255, 255), 
                                font=self.font, align="center", multiline=True)
        self.matrix.draw_text((25, 13), 'VS', font=self.font_large)

    def draw_live(self):
        # Get the Info
        period = self.scoreboard.periods.ordinal
        clock = self.scoreboard.periods.clock
        score = '{}-{}'.format(self.scoreboard.away_team.goals, self.scoreboard.home_team.goals)

        # Align the into with center of screen
        period_align = center_text(self.font.getsize(period)[0], 32)
        clock_align = center_text(self.font.getsize(clock)[0], 32)
        score_align = center_text(self.font_large.getsize(score)[0], 32)

        # Draw the info
        self.matrix.draw_text((period_align, -1), period, fill=(255, 255, 255), font=self.font, align="center", multiline=True)
        self.matrix.draw_text((clock_align, 5), clock, fill=(255, 255, 255), font=self.font, align="center", multiline=True)
        self.matrix.draw_text((score_align, 15), score, fill=(255, 255, 255), font=self.font_large, align="center", multiline=True)

    def draw_final(self):
        # Get the Info
        period = self.scoreboard.periods.ordinal
        result = self.scoreboard.periods.clock
        score = '{}-{}'.format(self.scoreboard.away_team.goals, self.scoreboard.home_team.goals)
        date = convert_date_format(self.scoreboard.date)

        # Align the into with center of screen
        date_align = center_text(self.font.getsize(date)[0], 32)
        score_align = center_text(self.font_large.getsize(score)[0], 32)

        # Draw the info
        self.matrix.draw_text((date_align, -1), date, fill=(255, 255, 255), font=self.font, align="center", multiline=True)
        if self.scoreboard.periods.number > 3:
            print("Hello")
            result_align = center_text(self.font.getsize("F/{}".format(period))[0], 32)
            self.matrix.draw_text((result_align, 5), "F/{}".format(period), fill=(255, 255, 255), font=self.font, align="center", multiline=True)
        else:
            result_align = center_text(self.font.getsize(result)[0], 32)
            self.matrix.draw_text((result_align, 5), result, fill=(255, 255, 255), font=self.font, align="center", multiline=True)

        self.matrix.draw_text((score_align, 15), score, fill=(255, 255, 255), font=self.font_large, align="center", multiline=True)

    def draw_Irregular(self):
        pass
