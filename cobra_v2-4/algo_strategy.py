import gamelib
import random
import math
import warnings
from sys import maxsize
import json


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        # This is a good place to do initial setup
        self.scored_on_locations = []

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        self.starter_strategy(game_state)

        game_state.submit_turn()


    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """

    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some interceptors early on.
        We will place turrets near locations the opponent managed to score on.
        For offense we will use long range demolishers if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Scouts to try and score quickly.
        """
        resources = game_state.get_resources()
        movement_points = resources[MP]
        structure_points = resources[SP]

        self.build_t1_defences(game_state)

        # Wait for 4 turns and build up movement points
        if game_state.turn_number > 4:
            if (game_state.turn_number < 16 or game_state.enemy_health < 15) and game_state.turn_number < 23:
                if (self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[14, 15, 16]) > 15
                and movement_points > 12 and structure_points > 15):
                    self.demolisher_line_strategy(game_state)
                # Only spawn Scouts every other turn
                elif game_state.turn_number % 2 == 1:
                    # To simplify we will just check sending them from back left and right
                    game_state.attempt_spawn(SCOUT, [13,0], 1000)
            # If we haven't won or made good progress by turn 18, try to break through with demolishers, then send scouts
            elif game_state.turn_number > 20:
                if game_state.turn_number % 5 == 0:
                    self.demolisher_push_strategy(game_state)
                elif game_state.turn_number % 5 == 1:
                    game_state.attempt_spawn(SCOUT, [13,0], 1000)

        self.build_t2_defences(game_state)
        self.build_t3_defences(game_state)

    def demolisher_line_strategy(self, game_state):
        """
        Build a line of the cheapest stationary unit so our demolisher can attack from long range.
        """
        for x in range(22, 5, -1):
            game_state.attempt_spawn(WALL, [x, 13])

        support_locations = [[24,11],[25,11]]
        game_state.attempt_spawn(SUPPORT,support_locations)
        game_state.attempt_upgrade(support_locations)

        game_state.attempt_spawn(DEMOLISHER, [24, 10], 1000)

    def build_t1_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        turret_locations = [[24,12],[21,10]]
        game_state.attempt_spawn(TURRET, turret_locations)

        wall_locations = [[5,8],[6,7],[7,7], [8,6], [9,5], [10,4], [11,3], [12,3], [15,3], [16,4], [17,5],
                          [18,6], [19,7], [20,8],[21,9]]
        game_state.attempt_spawn(WALL, wall_locations)

        support_locations = [[13,3], [14,3]]
        game_state.attempt_spawn(SUPPORT, support_locations)

    def build_t2_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download
        wall_locations = [[0, 13], [1, 12], [4, 9], [3, 10], [2, 11], [26, 13], [27, 13], [20,11], [20,10], [25,13]]
        game_state.attempt_spawn(WALL, wall_locations)

        turret_locations = [[23,12], [23,13], [24,13]]
        game_state.attempt_spawn(TURRET, turret_locations)

        upgrade_turret_locations = [[23,12],[21,10]]
        game_state.attempt_upgrade(upgrade_turret_locations)

        support_locations = [[13,2],[14,2],[14,4]]
        game_state.attempt_spawn(SUPPORT, support_locations)

    def build_t3_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy demolishers can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download
        wall_locations = [[22,13],[20,12]]
        game_state.attempt_spawn(WALL,wall_locations)
        upgrade_wall_locations = [[20,11],[20,10],[22,13],[20,12]]
        game_state.attempt_upgrade(upgrade_wall_locations)

        turret_locations =[[24,13], [22,10], [21,11]]
        game_state.attempt_spawn(TURRET, turret_locations)

        upgrade_turret_locations = [[23,13], [24,13], [23,13], [22,10], [21,11],[23,12], [22,10]]
        game_state.attempt_upgrade(upgrade_turret_locations)

        support_locations = [[15,4], [15,5], [16,5], [16,6], [17,6], [12,1], [13,1]]
        game_state.attempt_spawn(SUPPORT, support_locations)

        upgrade_support_locations = [[13,2], [13,3], [14,3], [14,2],[14,4],[15,4], [15,5], [16,5], [16,6], [17,6], [12,1], [13,1]]
        game_state.attempt_upgrade(upgrade_support_locations)

    def demolisher_push_strategy(self, game_state):
        """
        Try to smash through with demolishers, no need to build a line
        """
        game_state.attempt_spawn(DEMOLISHER, [13, 0], 1000)

    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to 
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy turrets that can attack each location and multiply by turret damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(TURRET, game_state.config).damage_i
            damages.append(damage)
        
        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units
        
    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called 
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at in json-docs.html in the root of the Starterkit.
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly, 
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
