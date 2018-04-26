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
GIANT_TYPE = 2

STRUCTURE_NONE = -1
STRUCTURE_MINE = 0
STRUCTURE_TOWER = 1
STRUCTURE_BARRACKS = 2

KNIGHT_PRICE = 80
ARCHER_PRICE = 100
GIANT_PRICE = 140


K_KNIGHT = "KNIGHT"
K_ARCHER = "ARCHER"
K_GIANT = "GIANT"

NONE = -1
INPUT = 0
ACTION = 1

last_build = None

class QueenAction(Enum):
    NONE = -1
    CREATE_MINE_CLOSEST = 1
    CREATE_ARCHER_BARRACKS = 10
    CREATE_KNIGHT_BARRACKS = 11
    CREATE_GIANT_BARRACKS = 12
    CREATE_KNIGHT_BARRACKS_ON_MID = 13
    CREATE_KNIGHT_BARRACKS_ON_ENEMY = 14
    CREATE_TOWER_CLOSEST = 20
    CREATE_MINE_OR_TOWER = 30


DESIRED_INCOME = 100


def log(text, key=NONE):
    pass
    if key == INPUT:
        # print("Input: {}".format(text), file=sys.stderr)
        pass
    elif key == ACTION:
        print("Action: {}".format(text), file=sys.stderr)
    else:
        print("Generic: {}".format(text), file=sys.stderr)

    # pass


class Point:
    def __init__(self, i_x=-1, i_y=-1):
        self.x = i_x
        self.y = i_y

    def __bool__(self):
        return self.x != -1 and self.y != -1


starting_point = Point()


class Unit(Point):
    def __init__(self, i_x, i_y, i_owner, i_unit_type, i_health):
        Point.__init__(self, i_x, i_y)
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
        self.gold_remaining = None
        self.max_mine_size = None
        self.structure_type = None
        self.owner = None
        self.param_1 = None
        self.param_2 = None

    def update(self, i_gold_remaining, i_max_mine_size, i_structure_type, i_owner, i_param_1, i_param_2):
        self.gold_remaining = i_gold_remaining
        self.max_mine_size = i_max_mine_size
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
        self.owned_giant_barracks = list()
        self.owned_avail_knight_barracks = list()
        self.owned_avail_archer_barracks = list()
        self.owned_avail_giant_barracks = list()
        self.enemy_knight_barracks = list()
        self.total_sites = 0
        self.total_income = 0
        self.desired_site = None

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
        self.owned_giant_barracks.clear()
        self.owned_avail_knight_barracks.clear()
        self.owned_avail_archer_barracks.clear()
        self.owned_avail_giant_barracks.clear()
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
                if i_param_2 == GIANT_TYPE:
                    self.owned_giant_barracks.append(i_site_id)
                    if i_param_1 == 0:
                        self.owned_avail_giant_barracks.append(i_site_id)
        elif i_owner == NEUTRAL:
            self.neutral_sites.append(i_site_id)


def is_non_friendly_buildable(i_site_id, i_sites: Sites):
    non_friend_buildings = list()
    find_not_friendly_buildable(i_sites, non_friend_buildings)
    for site in non_friend_buildings:
        log("Checking site {}".format(site.site_id))
        if i_site_id == site.site_id:
            return True
    return False


def find_closest_to_point(i_sites: list, i_point: Point):
    dist = 10000000
    closest_site = None
    for site in i_sites:
        dist_to_point = calc_distance(site, i_point)
        if dist_to_point < dist:
            dist = dist_to_point
            closest_site = site
    return closest_site


def find_not_friendly_buildable(i_sites: Sites, o_sites):
    for site_id in i_sites.neutral_sites:
        o_sites.append(i_sites[site_id])
        # log("Adding neutral {}".format(site_id))
    for site_id in i_sites.enemy_sites:
        if i_sites[site_id].structure_type != STRUCTURE_TOWER:
            o_sites.append(i_sites[site_id])
            # log("Adding enemy {}".format(site_id))


def find_closest_buildable_mine(i_sites: Sites, i_point: Point):
    available_sites = list()
    find_not_friendly_buildable(i_sites, available_sites)
    for site in i_sites.owned_mines:
        if i_sites[site].max_mine_size > i_sites[site].param_1:
            # log("Adding mine: {} to available sites".format(site))
            available_sites.append(i_sites[site])
    return find_closest_to_point(available_sites, i_point)


def find_closest_not_friendly_buildable_to_point(i_sites: Sites, i_point: Point):
    available_sites = list()
    find_not_friendly_buildable(i_sites, available_sites)
    return find_closest_to_point(available_sites, i_point)


def find_closest_neutral_to_point(i_sites: Sites, i_point: Point):
    return find_closest_to_point(i_sites.neutral_sites, i_point)


def get_init_sites(i_sites: Sites):
    i_num_sites = input()
    log("num_sites {}".format(i_num_sites), INPUT)
    num_sites = int(i_num_sites)
    for i in range(num_sites):
        i_site_info = input()
        log("site_info {}".format(i_site_info), INPUT)
        site_id, x, y, radius = [int(j) for j in i_site_info.split()]
        i_sites.insert(Site(site_id, x, y, radius))


def get_units(i_units: Units):
    global starting_point
    i_num_units = input()
    log("num_units {}".format(i_num_units), INPUT)
    num_units = int(i_num_units)
    i_units.clear()
    for i in range(num_units):
        # unit_type: -1 = QUEEN, 0 = KNIGHT, 1 = ARCHER
        i_unit_info = input()
        log("unit_info {}".format(i_unit_info), INPUT)
        x, y, owner, unit_type, health = [int(j) for j in i_unit_info.split()]
        if unit_type == QUEEN_TYPE:
            if owner == FRIENDLY:
                if not starting_point:
                    starting_point = Point(x, y)
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
        log("site_info {}".format(i_site_info), INPUT)
        site_id, gold_remaining, max_mine_size, structure_type, owner, param_1, param_2 = [int(j) for j in i_site_info.split()]
        i_sites.update(site_id, gold_remaining, max_mine_size, structure_type, owner, param_1, param_2)


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


def build_structure(site_id, i_structure_type, i_barracks_type=""):
    if i_structure_type == STRUCTURE_TOWER:
        print("BUILD {} TOWER".format(site_id))
    elif i_structure_type == STRUCTURE_MINE:
        print("BUILD {} MINE".format(site_id))
    elif i_structure_type == STRUCTURE_BARRACKS:
        print("BUILD {} BARRACKS-{}".format(site_id, i_barracks_type))


def move_or_construct(i_touched_site_id, i_sites: Sites, i_structure_type, i_barracks_type=""):
    log("touched site: {}, desired site: {}".format(i_touched_site_id, i_sites.desired_site.site_id))
    log("structure type: {}".format(i_structure_type))
    if i_touched_site_id == -1:
        move_to(i_sites.desired_site)
        return
    if i_touched_site_id == i_sites.desired_site.site_id:
        build_structure(i_touched_site_id, i_structure_type, i_barracks_type)
        i_sites.desired_site = None
        return
    if i_sites[i_touched_site_id].owner == FRIENDLY and\
            i_sites[i_touched_site_id].structure_type == STRUCTURE_TOWER and \
            i_sites[i_touched_site_id].param_1 < 350:
        build_structure(i_touched_site_id, STRUCTURE_TOWER)
        return
    if i_sites[i_touched_site_id].owner == FRIENDLY and \
            i_sites[i_touched_site_id].structure_type == STRUCTURE_MINE and \
            i_sites[i_touched_site_id].max_mine_size > i_sites[i_touched_site_id].param_1:
        build_structure(i_touched_site_id, STRUCTURE_MINE)
        return
    if is_non_friendly_buildable(i_touched_site_id, i_sites):
        build_structure(i_touched_site_id, STRUCTURE_TOWER)
        return
    move_to(i_sites.desired_site)


def create_mine_or_tower(i_touched_site_id, i_sites: Sites, i_units: Units):
    global last_build
    log("Creating mine or tower, last built {}".format(last_build), ACTION)
    if not i_sites.desired_site:
        i_sites.desired_site = find_closest_not_friendly_buildable_to_point(i_sites, starting_point)

    if i_sites.desired_site.gold_remaining < 50:
        log("low gold remaining", ACTION)
        move_or_construct(i_touched_site_id, i_sites, STRUCTURE_TOWER)
        last_build = STRUCTURE_TOWER
        return
    if i_sites.desired_site.max_mine_size > 2:
        log("high mine max size", ACTION)
        move_or_construct(i_touched_site_id, i_sites, STRUCTURE_MINE)
        last_build = STRUCTURE_MINE
        return
    if last_build == STRUCTURE_MINE:
        log("last was mine", ACTION)
        move_or_construct(i_touched_site_id, i_sites, STRUCTURE_TOWER)
        last_build = STRUCTURE_TOWER
        return
    log("No special condition", ACTION)
    move_or_construct(i_touched_site_id, i_sites, STRUCTURE_MINE)
    last_build = STRUCTURE_MINE


def create_mine_closest(i_touched_site_id, i_sites: Sites, i_units: Units):
    if not i_sites.desired_site:
        i_sites.desired_site = find_closest_buildable_mine(i_sites, starting_point)
    if i_sites.desired_site.gold_remaining < 50:
        log("low gold remaining", ACTION)
        move_or_construct(i_touched_site_id, i_sites, STRUCTURE_TOWER)
        i_sites.desired_site = find_closest_buildable_mine(i_sites, starting_point)
        return
    move_or_construct(i_touched_site_id, i_sites, STRUCTURE_MINE)


def create_barracks_closest(i_touched_site_id, i_sites: Sites, i_units: Units, barrack_type=K_ARCHER):
    if not i_sites.desired_site:
        i_sites.desired_site = find_closest_not_friendly_buildable_to_point(i_sites, starting_point)
    move_or_construct(i_touched_site_id, i_sites, STRUCTURE_BARRACKS, barrack_type)


def create_barracks_mid(i_touched_site_id, i_sites: Sites, i_units: Units, barrack_type=K_ARCHER):
    if not i_sites.desired_site:
        mid_point = get_mid_point(starting_point, i_units.enemy_queen)
        i_sites.desired_site = find_closest_not_friendly_buildable_to_point(i_sites, mid_point)
    move_or_construct(i_touched_site_id, i_sites, STRUCTURE_BARRACKS, barrack_type)


def create_knight_enemy(i_touched_site_id, i_sites: Sites, i_units: Units):
    if not i_sites.desired_site:
        i_sites.desired_site = i_sites[i_sites.enemy_knight_barracks[0]]
    move_or_construct(i_touched_site_id, i_sites, STRUCTURE_BARRACKS, K_KNIGHT)


def perform_queen_action(i_action: QueenAction, i_touched_site_id, i_sites: Sites, i_units: Units):
    if i_action == QueenAction.CREATE_MINE_CLOSEST:
        create_mine_closest(i_touched_site_id, i_sites, i_units)
    elif i_action == QueenAction.CREATE_ARCHER_BARRACKS:
        create_barracks_closest(i_touched_site_id, i_sites, i_units, K_ARCHER)
    elif i_action == QueenAction.CREATE_KNIGHT_BARRACKS:
        create_barracks_closest(i_touched_site_id, i_sites, i_units, K_KNIGHT)
    # elif i_action == QueenAction.CREATE_GIANT_BARRACKS:
    #     create_barracks_closest(i_touched_site_id, i_sites, i_units, K_GIANT)
    elif i_action == QueenAction.CREATE_KNIGHT_BARRACKS_ON_MID:
        create_barracks_mid(i_touched_site_id, i_sites, i_units, K_KNIGHT)
    elif i_action == QueenAction.CREATE_KNIGHT_BARRACKS_ON_ENEMY:
        create_knight_enemy(i_touched_site_id, i_sites, i_units)
    else:
        create_mine_or_tower(i_touched_site_id, i_sites, i_units)


# Get action
def enough_mines(i_sites: Sites):
    if i_sites.total_income < 3:
        return False
    return True


def find_action(i_sites: Sites, i_units: Units):
    if not i_sites.owned_archer_barracks:
        return QueenAction.CREATE_ARCHER_BARRACKS
    if not i_sites.owned_knight_barracks:
        return QueenAction.CREATE_KNIGHT_BARRACKS_ON_MID
    if not enough_mines(i_sites):
        return QueenAction.CREATE_MINE_CLOSEST
    if not i_sites.owned_giant_barracks:
        return QueenAction.CREATE_GIANT_BARRACKS
    # if i_sites.enemy_knight_barracks:
    #     return QueenAction.CREATE_KNIGHT_BARRACKS_ON_ENEMY
    return QueenAction.CREATE_MINE_OR_TOWER


def queen_action(i_touched_site_id, i_sites: Sites, i_units: Units):
    action_to_do = find_action(i_sites, i_units)
    log("action: {}".format(action_to_do.name), ACTION)
    perform_queen_action(action_to_do, i_touched_site_id, i_sites, i_units)


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
    if len(i_sites.owned_avail_knight_barracks) != 0 and i_units.count_owned_knights() < 9:
        max_buildable = int(i_gold / KNIGHT_PRICE)
        if max_buildable > 0:
            sites_to_train.append(i_sites.owned_avail_knight_barracks[0])
            i_gold -= KNIGHT_PRICE
    if len(i_sites.owned_avail_archer_barracks) != 0:
        max_buildable = int(i_gold / ARCHER_PRICE)
        if max_buildable > 0:
            sites_to_train.append(i_sites.owned_avail_archer_barracks[0])
            i_gold -= ARCHER_PRICE
    if len(i_sites.owned_avail_giant_barracks) != 0:
        max_buildable = int(i_gold / GIANT_PRICE)
        if max_buildable > 0:
            sites_to_train.append(i_sites.owned_avail_giant_barracks[0])
            i_gold -= GIANT_PRICE
    run_train(sites_to_train)


sites = Sites()
units = Units()
get_init_sites(sites)
# game loop
while True:
    # touched_site: -1 if none
    i_extra_input = input()
    log("extra_input {}".format(i_extra_input), INPUT)
    gold, touched_site_id = [int(i) for i in i_extra_input.split()]
    get_sites(sites)
    get_units(units)

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    # First line: A valid queen action
    # Second line: A set of training instructions
    queen_action(touched_site_id, sites, units)
    training_action(sites, units, gold)
