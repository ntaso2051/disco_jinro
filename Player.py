from Jobs.Seer import Seer
from Jobs.Villager import Villager
from Jobs.Werewolf import Werewolf
from Jobs.Knight import Knight
from Jobs.Madman import Madman


class Player():
    def __init__(self, id, name, jname):
        self.id = id
        self.name = name
        self.reset()
        if jname == 'Villager':
            self.job = Villager()
            self.is_wolf = False
            self.is_side = 0
        if jname == 'Werewolf':
            self.job = Werewolf()
            self.is_wolf = True
            self.is_side = 1
        if jname == 'Seer':
            self.job = Seer()
            self.is_wolf = False
            self.is_side = 0
        if jname == 'Knight':
            self.job = Knight()
            self.is_wolf = False
            self.is_side = 0
        if jname == 'Madman':
            self.job = Madman()
            self.is_wolf = False    
            self.is_side = 1

    def act(self, target):
        self.acted = True
        text = self.job.night_act(target)
        return text

    def vote(self, p):
        self.voted = True
        self.voted_target = p.get_name()

    def reset(self):
        self.acted = False
        self.voted = False
        self.voted_target = ''
        self.dead = False
        self.covered = False

    def get_is_wolf(self):
        return self.is_wolf
    
    def get_is_side(self):
        return self.is_side

    def is_voted(self):
        return self.voted

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id

    def get_job(self):
        return self.job.get_display_name()

    def get_job_name(self):
        return self.job.get_name()

    def is_dead(self):
        return self.dead

    def set_dead(self, ok):
        self.dead = ok

    def is_covered(self):
        return self.covered

    def set_covered(self, ok):
        self.covered = ok

    def is_acted(self):
        return self.acted

    def set_acted(self, ok):
        self.acted = ok

    def message(self):
        return self.job.night_message()

    def morning(self):
        self.covered = False
        self.voted = False
        self.voted_target = ''
        self.acted = False

    def get_voted_target(self):
        return self.voted_target
