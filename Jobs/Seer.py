from Jobs.Job import Job


class Seer(Job):
    def __init__(self):
        self.name = 'Seer'
        self.display_name = '占い師'

    def night_act(self, target):
        text = target.get_name()
        if target.get_is_wolf():
            text += 'は人狼陣営です'
        else:
            text += 'は村人陣営です'
        return text

    def night_message(self):
        return '占いたい相手を指定してください。'
