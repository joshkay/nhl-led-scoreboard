from datetime import datetime, timedelta
import nhl_api_parser as nhlparser
import debug

class Data:
    def __init__(self, config):

        self.idex = 0
        # Save the parsed config
        self.config = config

        # Flag to determine when to refresh data
        self.needs_refresh = True

        # Flag to determine when it's a new day
        self.new_day = False

        # get favorite team's id
        self.fav_team_id = self.config.fav_team_id

        # Used to set the current game displayed
        self.current_team_id = self.fav_team_id

        # Flag to display goal horn
        self.home_team_goal = False
        self.away_team_goal = False

        self.overview = 0

        # Parse today's date and see if we should use today or yesterday
        self.get_current_date()

        # Fetch the teams info
        self.get_teams_info = nhlparser.get_teams()

        # Fetch the games for today
        self.refresh_games = nhlparser.fetch_games()

        # Look if favorite team play today
        self.refresh_fav_team_status()
 
    def __parse_today(self):
        today = datetime.today()
        end_of_day = datetime.strptime(self.config.end_of_day, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
        if end_of_day > datetime.now():
            today -= timedelta(days=1)

        return today.year, today.month, today.day

    def set_date(self):
        return datetime(self.year, self.month, self.day)

    def get_current_date(self):
        self.year, self.month, self.day = self.__parse_today()

    def refresh_overview(self):
        overview = nhlparser.fetch_overview(self.current_team_id)
        debug.info(overview['time'])

        self.home_team_goal = False
        self.away_team_goal = False

        if (self.overview != 0 and 
            overview['away_team_id'] == self.overview['away_team_id'] and 
            overview['home_team_id'] == self.overview['home_team_id']):
            # Check if goal is scored
            
            if (overview['home_score'] > self.overview['home_score']):
                self.home_team_goal = True
            if (overview['away_score'] > self.overview['away_score']):
                self.away_team_goal = True
            
        self.overview = overview
        self.needs_refresh = False

    def get_schedule(self):
        self.schedule = nhlparser.fetch_fav_team_schedule(self.current_team_id)

    def refresh_fav_team_status(self):
        self.fav_team_game_today = nhlparser.check_if_game(self.current_team_id)

    def check_fav_team_next_game(self):
        pass

    def set_fav_team_id(self, fav_team_id):
        self.fav_team_id = fav_team_id
     
    def get_fav_team_id(self):
        return self.fav_team_id

    def set_current_team_id(self, current_team_id):
        self.current_team_id = current_team_id

    def get_current_team_id(self):
        return self.current_team_id
    
    def get_lastgame(self):
        self.lastgame = nhlparser.fetch_fav_team_lastgame(self.fav_team_id)
