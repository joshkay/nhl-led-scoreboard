from datetime import datetime, timedelta
from time import sleep
import debug
import nhl_api
from data.status import Status
from data.scoreboard import Scoreboard

NETWORK_RETRY_SLEEP_TIME = 10

class Data:
    def __init__(self, config):
        """
            TODO:
                - Add Delay option to match the TV broadcast
                - Add a network issues handler. (Show Red bar at bottom of screen)
                - Add Playoff data info. (research required)
                - Add Powerplay info (research required)
                - Make a Shootout layout with check boxes for each attempt
        :param config:
        """
        # Save the parsed config
        self.config = config
        self.refresh_data()

    def refresh_data(self):
        # Flag to determine when to refresh data
        self.needs_refresh = True

        # Flag for network issues
        self.network_issues = False

        # Get all the team's info
        self.get_teams_info()

        # get favorite team's id
        self.pref_teams = self.get_pref_teams_id()

        # Used to set the current game displayed
        self.current_team_id = self.fav_team_id

        # Flag to display goal horn
        self.home_team_goal = False
        self.away_team_goal = False

        self.overview = 0

        # Parse today's date and see if we should use today or yesterday
        self.refresh_current_date()

        # Set the pointer to the first game in the list of Pref Games
        self.current_game_index = 0

        # Fetch the games for today
        self.refresh_games()

        # Today's date
        self.today = self.date()

        # Get the status from the API
        self.get_status()

        # Get refresh standings
        self.refresh_standings()
    #
    # Date

    def __parse_today(self):
        today = datetime.today()
        end_of_day = datetime.strptime(self.config.end_of_day, "%H:%M").replace(year=today.year, month=today.month,
                                                                                day=today.day)
        if end_of_day > datetime.now():
            today -= timedelta(days=1)

        return today.year, today.month, today.day

    def date(self):
        return datetime(self.year, self.month, self.day).date()

    def refresh_current_date(self):
        self.year, self.month, self.day = self.__parse_today()

    def _is_new_day(self):
        self.refresh_current_date()
        if self.today != self.date():
            self.refresh_data()
            return True
        else:
            return False

    #
    # Daily NHL Data

    def refresh_games(self):
        """
            Refresh the current list of games of the day.

            self.games : List of all the games happening today
            self.pref_games : List of games which the preferred teams are ordered by priority.

            If the user want's to rotate only his preferred games between the periods and during the day, save those
            only. Lastly, If if not an Off day for the pref teams, reorder the list in order of preferred teams and load
            the first game as the main event.
        """
        attempts_remaining = 5
        while attempts_remaining > 0:
            try:
                self.games = nhl_api.day(self.year, self.month, self.day)
                self.pref_games = self.__filter_list_of_games(self.games, self.pref_teams)
                if self.config.preferred_teams_only and self.pref_teams:
                    self.games = self.pref_games

                if not self.is_pref_team_offday():
                    self.pref_games = self.__prioritize_pref_games(self.pref_games, self.pref_teams)
                    self.current_game_id = self.pref_games[self.current_game_index].game_id

                self.network_issues = False
                break
            except ValueError as error_message:
                self.network_issues = True
                debug.error("Failed to refresh the list of games. {} attempt remaining.".format(attempts_remaining))
                debug.error(error_message)
                attempts_remaining -= 1
                sleep(NETWORK_RETRY_SLEEP_TIME)

    # This is the function that will determine the state of the board (Offday, Gameday, Live etc...).
    def get_status(self):
        self.status = Status()

    def __filter_list_of_games(self, games, teams):
        """
        Filter the list 'games' and keep only the games which the teams in the list 'teams' are part of.
        """
        return list(game for game in set(games) if {game.away_team_id, game.home_team_id}.intersection(set(teams)))

    def __prioritize_pref_games(self, games, teams):
        """
        This one is a doozy. If you find a cleaner or more efficient way, please let me know.

        Order list of preferred games to match the order of their corresponding team and clean the 'None' element
        produced by the'map' function.

        return the cleaned game list. lemony fresh!!!
        """

        ordered_game_list = map(lambda team: next(
            (game for game in games if game.away_team_id == team or game.home_team_id == team), None),
                                teams)
        cleaned_game_list = list(filter(None, list(dict.fromkeys(ordered_game_list))))
        return cleaned_game_list

    #
    # Main game event data

    def refresh_overview(self):
        """
            Get a all the data of the main event.
        :return:
        """
        attempts_remaining = 5
        while attempts_remaining > 0:
            try:
                self.overview = nhl_api.overview(self.current_game_id)
                self.needs_refresh = False
                self.network_issues = False
                break
            except ValueError as error_message:
                self.network_issues = True
                debug.error("Failed to refresh the Overview. {} attempt remaining.".format(attempts_remaining))
                debug.error(error_message)
                attempts_remaining -= 1
                sleep(NETWORK_RETRY_SLEEP_TIME)

    def advance_to_next_game(self):
        """
        function to show the next game of in the "games" list.

        Check the status of the current preferred game and if it's Final or between periods rotate to the next game on
        the game list.

        :return:
        """
        pass

    def __next_game_index(self):
        counter = self.current_game_index + 1
        if counter >= len(self.games):
            counter = 0
        return counter

    #
    # Standings

    def refresh_standings(self):
        self.standings = nhl_api.standings()

    #
    # Teams

    def get_teams_info(self):
        self.teams = nhl_api.teams()
        info_by_id = {}
        for team in self.teams:
            info_by_id[team.team_id] = team

        self.teams_info = info_by_id


    def get_pref_teams_id(self):
        """
            Finds the preferred teams ID. The type of Team information variate throughout the API except for the team's id.
            Working with that will be much easier.

        :return: list of the preferred team's ID in order
        """

        allteams = self.teams
        pref_teams = self.config.preferred_teams
        allteams_id = {}
        pref_teams_id = []
        # Put all the team's in a dict with there name as KEY and ID as value.
        for team in allteams:
            allteams_id[team.team_name] = team.team_id

        # Go through the list of preferred teams name. If the team's name exist, put the ID in a new list.
        if pref_teams:
            for team in pref_teams:
                if team in allteams_id:
                    pref_teams_id.append(allteams_id[team])
                else:
                    debug.warning(team + " is not a team of the NHL. Make sure you typed team's name properly")

            return pref_teams_id
        else:
            return False

    #
    # Offdays

    def is_pref_team_offday(self):
        try:
            return not len(self.pref_games)
        except:
            return True

    def is_nhl_offday(self):
        try:
            return not len(self.games)
        except:
            return True

    #
    # Debugging
    def debug_overview(self):
        ## Test refresh Overview
        self.refresh_overview()
        ## Test scoreboard.py
        debug.log("Off day for preferred team: {}".format(self.is_pref_team_offday()))
        debug.log(self.status.is_offseason(self.date()))
        debug.log(Scoreboard(self.overview, self))
