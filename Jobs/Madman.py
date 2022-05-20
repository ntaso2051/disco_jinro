from Jobs.Job import Job


class Madman(Job):
    def __init__(self):
        self.name = 'Madman'
        self.display_name = '狂人'

    def night_act(self, target):
        return target.get_name() + 'が人狼だといいですね＾＾'

    def night_message(self):
        return '人狼だと思う人を一人指定してください。'