from Jobs.Job import Job


class Werewolf(Job):
    def __init__(self):
        self.name = 'Werewolf'
        self.display_name = '人狼'

    def night_act(self, target):
        if not target.is_covered():
            target.set_dead(True)
        return target.get_name() + ' さんを襲います。'

    def night_message(self):
        return '襲いたい相手を一人選んでください。'
