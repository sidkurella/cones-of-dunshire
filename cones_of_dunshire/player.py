from enum import Enum, auto
import json

class Role(Enum):
    LEDGERMAN = 0
    MAVERICK  = 1
    WIZARD    = 2
    CORPORAL  = 3
    ARBITER   = 4
    WARRIOR   = 5
    SHAMAN    = 6
    FARMER    = 7
    ALCHEMIST = 8
    BRINKSMAN = 9
    PROVOST   = 10
    ABBOTT    = 11
    DENIER    = 12

    def __str__(self):
        return self.name.title()

class Resource(Enum):
    LUMBER = 0
    WHEAT  = 1
    MEAT   = 2
    DAIRY  = 3
    WATER  = 4
    WOOL   = 5
    HORSES = 6
    GEMS   = 7
    IRON   = 8
    COAL   = 9

    def __str__(self):
        return self.name.title()

    def is_agriculture(self):
        return any(
            self == x for x in (Resource.WHEAT, Resource.MEAT, Resource.DAIRY)
        )

    def is_livestock(self):
        return any(
            self == x for x in (Resource.WOOL, Resource.HORSES)
        )

    def is_mined(self):
        return any(
            self == x for x in (Resource.GEMS, Resource.IRON, Resource.COAL)
        )


class Player:
    def __init__(self, id_number, name, role):
        self.id = id_number
        self.name = name
        self.role = role
        self.resources = [
            0 for _ in Resource
        ]

    def to_json(self):
        return json.dumps({
            'id':        self.id,
            'name':      self.name,
            'role':      self.role.value,
            'resources': self.resources,
        })

    @staticmethod
    def from_json(js):
        d = json.loads(js)
        p = Player(d['id'], d['name'], Role(d['role']))
        p.resources = d['resources']
        return p

