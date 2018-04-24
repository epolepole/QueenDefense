import sys
import math
from enum import Enum

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

NEUTRAL = -1
FRIENDLY = 0
ENEMY = 1

QUEEN_TYPE = -1
KNIGHT_TYPE = 0
ARCHER_TYPE = 1

STRUCTURE_NONE = 0
STRUCTURE_TOWER = 1
STRUCTURE_BARRACKS = 2
STRUCTURE_MINE = 3

KNIGHT_PRICE = 80
ARCHER_PRICE = 100
GIANT_PRICE = 140


K_KNIGHT = "KNIGHT"
K_ARCHER = "ARCHER"

class QueenAction(Enum):
    NONE = -1
    CREATE_MINE_CLOSEST = 1
    UPGRADE_MINE_CLOSEST = 2
    CREATE_ARCHER_BARRACKS = 10
    CREATE_KNIGHT_BARRACKS_ON_MID = 11
    CREATE_KNIGHT_BARRACKS_ON_THEIRS = 12
    CREATE_TOWER_CLOSEST = 20
    UPGRADE_TOWER_CLOSEST = 21




DESIRED_INCOME = 100


def log(text):
    # print(text, file=sys.stderr)
    pass


class Point:
    def __init__(self, i_x, i_y):
        self.x = i_x
        self.y = i_y


class Unit:
    def __init__(self, i_x, i_y, i_owner, i_unit_type, i_health):
        self.x = i_x
        self.y = i_y
        self.owner = i_owner
        self.unit_type = i_unit_type
        self.health = i_health


class Units:
    def __init__(self):
        self.queen = None
        self.enemy_queen = None
        self.enemies = list()
        self.allies = list()

    def clear(self):
        self.enemies.clear()
        self.allies.clear()

    def count_owned_archers(self):
        count = 0
        for unit in self.allies:
            if unit.unit_type == ARCHER_TYPE:
                count += 1
        return count

    def count_owned_knights(self):
        count = 0
        for unit in self.allies:
            if unit.unit_type == KNIGHT_TYPE:
                count += 1
        return count


class Site:
    def __init__(self, i_site_id, i_x, i_y, i_radius):
        self.site_id = i_site_id
        self.x = i_x
        self.y = i_y
        self.radius = i_radius
        self.ignore_1 = None
        self.ignore_2 = None
        self.structure_type = None
        self.owner = None
        self.param_1 = None
        self.param_2 = None

    def update(self, i_ignore_1, i_ignore_2, i_structure_type, i_owner, i_param_1, i_param_2):
        self.ignore_1 = i_ignore_1
        self.ignore_2 = i_ignore_2
        self.structure_type = i_structure_type
        self.owner = i_owner
        self.param_1 = i_param_1
        self.param_2 = i_param_2


class Sites:
    def __init__(self):
        self.sites_dict = dict()
        self.enemy_sites = list()
        self.owned_sites = list()
        self.neutral_sites = list()
        self.owned_mines = list()
        self.owned_knight_barracks = list()
        self.owned_archer_barracks = list()
        self.owned_avail_knight_barracks = list()
        self.owned_avail_archer_barracks = list()
        self.enemy_knight_barracks = list()
        self.total_sites = 0
        self.total_income = 0

    def __getitem__(self, key):
        return self.sites_dict[key]

    def __len__(self):
        return self.total_sites

    def clear(self):
        self.enemy_sites.clear()
        self.owned_sites.clear()
        self.neutral_sites.clear()
        self.owned_mines.clear()
        self.owned_knight_barracks.clear()
        self.owned_archer_barracks.clear()
        self.owned_avail_knight_barracks.clear()
        self.owned_avail_archer_barracks.clear()
        self.enemy_knight_barracks.clear()
        self.total_income = 0

    def insert(self, i_site: Site):
        self.sites_dict[i_site.site_id] = i_site
        if i_site.owner == ENEMY:
            self.enemy_sites.append(i_site.site_id)
        elif i_site.owner == FRIENDLY:
            self.owned_sites.append(i_site.site_id)
        elif i_site.owner == NEUTRAL:
            self.neutral_sites.append(i_site.site_id)
        self.total_sites = len(self.sites_dict)

    def update(self, i_site_id, i_ignore_1, i_ignore_2, i_structure_type, i_owner, i_param_1, i_param_2):
        self.sites_dict[i_site_id].update(i_ignore_1, i_ignore_2, i_structure_type, i_owner, i_param_1, i_param_2)
        if i_owner == ENEMY:
            self.enemy_sites.append(i_site_id)
            if i_structure_type == STRUCTURE_BARRACKS:
                self.enemy_knight_barracks.append(i_site_id)
        elif i_owner == FRIENDLY:
            self.owned_sites.append(i_site_id)
            if i_structure_type == STRUCTURE_MINE:
                self.owned_mines.append(i_site_id)
                self.total_income += i_param_1
            if i_structure_type == STRUCTURE_BARRACKS:
                if i_param_2 == ARCHER_TYPE:
                    self.owned_archer_barracks.append(i_site_id)
                    if i_param_1 == 0:
                        self.owned_avail_archer_barracks.append(i_site_id)
                if i_param_2 == KNIGHT_TYPE:
                    self.owned_knight_barracks.append(i_site_id)
                    if i_param_1 == 0:
                        self.owned_avail_knight_barracks.append(i_site_id)
        elif i_owner == NEUTRAL:
            self.neutral_sites.append(i_site_id)




def find_closest_neutral_to_point(i_sites: Sites, i_point):
    dist = 10000000
    closest_site = None
    for site_id in i_sites.neutral_sites:
        dist_to_queen = calc_distance(i_sites[site_id], i_point)
        if dist_to_queen < dist:
            dist = dist_to_queen
            closest_site = i_sites[site_id]
    return closest_site


def get_init_sites(i_sites: Sites):
    i_num_sites = input()
    log("num_sites {}".format(i_num_sites))
    num_sites = int(i_num_sites)
    for i in range(num_sites):
        i_site_info = input()
        log("site_info {}".format(i_site_info))
        site_id, x, y, radius = [int(j) for j in i_site_info.split()]
        i_sites.insert(Site(site_id, x, y, radius))


def get_units(i_units: Units):
    i_num_units = input()
    log("num_units {}".format(i_num_units))
    num_units = int(i_num_units)
    i_units.clear()
    for i in range(num_units):
        # unit_type: -1 = QUEEN, 0 = KNIGHT, 1 = ARCHER
        i_unit_info = input()
        log("unit_info {}".format(i_unit_info))
        x, y, owner, unit_type, health = [int(j) for j in i_unit_info.split()]
        if unit_type == QUEEN_TYPE:
            if owner == FRIENDLY:
                i_units.queen = Unit(x, y, owner, unit_type, health)
            elif owner == ENEMY:
                i_units.enemy_queen = Unit(x, y, owner, unit_type, health)
        if owner == FRIENDLY:
            i_units.allies.append(Unit(x, y, owner, unit_type, health))
        elif owner == ENEMY:
            i_units.enemies.append(Unit(x, y, owner, unit_type, health))


def get_sites(i_sites: Sites):
    i_sites.clear()
    for i in range(len(i_sites)):
        # ignore_1: used in future leagues
        # ignore_2: used in future leagues
        # structure_type: -1 = No structure, 2 = Barracks
        # owner: -1 = No structure, 0 = Friendly, 1 = Enemy
        i_site_info = input()
        log("site_info {}".format(i_site_info))
        site_id, ignore_1, ignore_2, structure_type, owner, param_1, param_2 = [int(j) for j in i_site_info.split()]
        i_sites.update(site_id, ignore_1, ignore_2, structure_type, owner, param_1, param_2)


def calc_distance(item_a, item_b):
    dx = item_a.x - item_b.x
    dy = item_a.y - item_b.y
    return math.sqrt(dx*dx + dy*dy)


def get_mid_point(item_a, item_b):
    return Point(item_a.x + (item_b.x - item_a.x)/2,
                 item_a.y + (item_b.y - item_a.y) / 2)


def move_to(place):
    print("MOVE {} {}".format(place.x, place.y))


def move_to_closest_neutral(i_sites: Sites, i_units: Units):
    move_to(find_closest_neutral_to_point(i_sites, i_units.queen))


def build_barracks(site_id, i_type):
    print("BUILD {} BARRACKS-{}".format(site_id, i_type))


def build_tower(site_id):
    print("BUILD {} TOWER".format(site_id))


def build_mine(site_id):
    print("BUILD {} MINE".format(site_id))


desired_site = None


def can_build_tower(i_touched_site, i_sites: Sites):
    if i_touched_site == -1:
        return False
    if desired_site and i_touched_site != desired_site.site_id:
        return True
    if i_sites[i_touched_site].owner == FRIENDLY and i_sites[i_touched_site].structure_type == STRUCTURE_TOWER:
        return True
    if i_sites[i_touched_site].owner == ENEMY and i_sites[i_touched_site].structure_type != STRUCTURE_TOWER:
        return True
    if i_sites[i_touched_site].owner == NEUTRAL and i_sites[i_touched_site].structure_type == STRUCTURE_TOWER:
        return True
    return False


def can_build_mine(i_touched_site, i_sites: Sites):
    if i_touched_site == -1:
        return False
    if i_sites[i_touched_site].owner == ENEMY and i_sites[i_touched_site].structure_type != STRUCTURE_TOWER:
        return True
    if i_sites[i_touched_site].owner == NEUTRAL:
        return True
    if i_sites[i_touched_site].owner == FRIENDLY and i_sites[i_touched_site].structure_type != STRUCTURE_MINE:
        return True
    return False



# def find_closest_buildable_mine_to_point(i_sites: Sites, i_point):
    # for site in i_sites.sites_dict.values():
        # if


# def maintain_one_mine(i_touched_site, i_sites: Sites, i_units: Units):
    # if i_sites.owned_mines and i_sites[i_sites.owned_mines[0]].


# def perform_queen_action(i_action: QueenAction, i_touched_site, i_sites: Sites, i_units: Units):
#     if i_action == QueenAction.CREATE_MINE_CLOSEST:
#         if can_build_mine(i_touched_site, sites):
#             build_mine(i_touched_site)
    #     elif:
    #
    #
    # if i_action == QueenAction.CREATE_ARCHER_BARRACKS:
    # if i_action == QueenAction.CREATE_KNIGHT_BARRACKS_ON_MID:
    # if i_action == QueenAction.CREATE_KNIGHT_BARRACKS_ON_THEIRS:
    # if i_action == QueenAction.CREATE_TOWER_CLOSEST:
    # if i_action == QueenAction.CREATE_MINE_CLOSEST:


def queen_action(i_touched_site, i_sites: Sites, i_units: Units):
    global desired_site
    # if there are no buildings build the first archery
    if len(i_sites.owned_archer_barracks) == 0:
        if i_touched_site == -1 or i_sites[i_touched_site].owner != NEUTRAL:
            move_to_closest_neutral(i_sites, i_units)
            return
        if i_sites[i_touched_site].owner != FRIENDLY:
            build_barracks(i_touched_site, K_ARCHER)
            return

    if can_build_tower(i_touched_site, sites):
        build_tower(i_touched_site)
        return

    # if there are no knight barracks go to build the first one at the mid point with the enemy queen
    if len(i_sites.owned_knight_barracks) == 0:
        if not desired_site:
            desired_site = find_closest_neutral_to_point(i_sites, get_mid_point(i_units.queen, i_units.enemy_queen))
        if i_touched_site != desired_site.site_id:
            move_to(desired_site)
            return
        else:
            build_barracks(i_touched_site, K_KNIGHT)
            desired_site = None
            return

    # if we have one of each, move back to first point, away from enemy
    # move_to(i_sites[i_sites.owned_archer_barracks[0]])
    if len(i_sites.enemy_knight_barracks) != 0:
        move_to(i_sites[i_sites.enemy_knight_barracks[0]])
        return
    move_to(i_sites[i_sites.neutral_sites[0]])
    return


# def get_owned_buildable_sites(i_sites: dict):
#     owned_sites = dict()
#     for site_id, site in i_sites.items():
#         if site.owner == FRIENDLY and site.param_1 == 0:
#             owned_sites[site_id] = site
#     return owned_sites
#
#
# def get_max_buildable(i_sites: dict, max_count):
#     buildable_sites = dict()
#     count = 1
#     for site_id, site in i_sites.items():
#         if count <= max_count:
#             buildable_sites[site_id] = site
#         count += 1
#     return buildable_sites
#
#
# def train_all_sites(i_sites, i_gold):
#     owned_sites = get_owned_buildable_sites(i_sites)
#     max_buildable = int(i_gold/80)
#     buildable_sites = get_max_buildable(owned_sites, max_buildable)
#     run_train(buildable_sites)


def dict_keys_to_str(a_keys_list: list):
    str_to_ret = ""
    for a_key in a_keys_list:
        str_to_ret += "{} ".format(a_key)
    if len(str_to_ret) != 0:
        str_to_ret = str_to_ret[:-1]
    return str_to_ret


def run_train(i_sites_ids: list):
    keys = dict_keys_to_str(i_sites_ids)
    if len(keys) != 0:
        print("TRAIN {}".format(keys))
    else:
        print("TRAIN")


def training_action(i_sites: Sites, i_units: Units, i_gold):

    sites_to_train = list()
    # if we have no knights but available knight barracks, train them
    if len(i_sites.owned_avail_knight_barracks) != 0 and i_units.count_owned_knights() < 7:
        max_buildable = int(i_gold / KNIGHT_PRICE)
        if max_buildable > 0:
            sites_to_train.append(i_sites.owned_avail_knight_barracks[0])
            i_gold -= KNIGHT_PRICE
    if len(i_sites.owned_avail_archer_barracks) != 0:
        max_buildable = int(i_gold / ARCHER_PRICE)
        if max_buildable > 0:
            sites_to_train.append(i_sites.owned_avail_archer_barracks[0])
            i_gold -= ARCHER_PRICE
    run_train(sites_to_train)


sites = Sites()
units = Units()
get_init_sites(sites)

# game loop
while True:
    # touched_site: -1 if none
    i_extra_input = input()
    log("extra_input {}".format(i_extra_input))
    gold, touched_site = [int(i) for i in i_extra_input.split()]
    get_sites(sites)
    get_units(units)

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    # First line: A valid queen action
    # Second line: A set of training instructions
    queen_action(touched_site, sites, units)
    training_action(sites, units, gold)
