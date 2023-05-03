from abc import ABC, abstractmethod


class GameInterface(ABC):

    @abstractmethod
    def generate_next_states(self):
        pass

    @abstractmethod
    def game_over(self):
        pass

    @abstractmethod
    def random_move(self):
        pass

    @abstractmethod
    def get_final_reward(self):
        pass
