from Jobs.Job import Job


class Bakery(Job):
    def __init__(self):
        self.name = 'Bakery'
        self.display_name = 'パン屋'

    def night_act(self, target):
        return target.get_name() + 'が人狼だといいですね＾＾'

    def night_message(self):
        return '人狼だと思う人を一人指定してください。'