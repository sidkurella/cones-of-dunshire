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

class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def to_json(self):
        name = self.name
        role = self.role.value
        return f'{{"name":"{name}","role":{role}}}'

    @staticmethod
    def from_json(js):
        d = json.loads(js)
        return Player(d['name'], Role(d['role']))

