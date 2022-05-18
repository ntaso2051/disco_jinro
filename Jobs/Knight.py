from Jobs.Job import Job


class Knight(Job):
    def __init__(self):
        self.name = 'Knight'
        self.display_name = '狩人'

    def night_act(self, target):
        target.set_covered(True)
        return 'を護ります。'

    def night_message(self):
        return '護りたい人を一人指定してください。'
