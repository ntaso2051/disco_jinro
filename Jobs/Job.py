from abc import ABCMeta, abstractmethod


class Job(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def night_act(self, target):
        pass

    @abstractmethod
    def night_message(self):
        pass

    def get_name(self):
        return self.name

    def get_display_name(self):
        return self.display_name
