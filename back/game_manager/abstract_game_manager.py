from abc import ABC, abstractmethod

from .game_element import GameElement
from .fixed_size_queue import FixedSizeQueue
from .fixed_size_set import FixedSizeSet
from .region import Region
from .statistics_manager import StatisticsManager


class AbstractGameManager(GameElement, ABC):
    def __init__(self,
                 players_max,
                 regions_max,
                 to_create_room=None):

        super().__init__()
        if to_create_room:
            self._to_create_room = to_create_room
        else:
            self._to_create_room = int(players_max / 2)
        self._players = FixedSizeQueue(maxlen=players_max)
        self._regions = FixedSizeSet(maxlen=regions_max)
        self._stats_manager = StatisticsManager()

    @abstractmethod
    def most_effective_region_for_player(self, player):
        pass

    @abstractmethod
    def most_effective_region_for_room(self, room_name, player):
        pass

    @property
    def in_queue(self):
        return self._players.size

    @property
    def region_name(self):
        return [region.name for region in self._regions]

    @property
    def stats(self):
        return self._stats_manager.to_dict()

    def to_dict(self):
        return {"max_players": self._players.capacity,
                "max_region": self._regions.maxlen,
                "queue": [player.to_dict() for player in self._players],
                "regions": [region.to_dict() for region in self._regions]}

    def player_names(self):
        return set(reduce(lambda current_names, new_names: current_names.update(new_names),
                          [region.player_names() for region in self._regions]))

    def add_region(self, region):
        if not self.has_region(region.name) and self._regions.has_place():
            return self._regions.add(region)

    def has_region(self, region_name):
        return self._regions.find_by_lambda(lambda region: region_name == region.name)

    def remove_region(self, region_name):
        return self._regions.remove_lambda(lambda region: region_name == region.name)

    def add_player(self, player):
        if self._can_add_player(player):
            self._stats_manager.player_start(player)
            region = self.most_effective_region_for_player(player)
            if region:
                return region.add_player(player)
            elif self._players.can_push() and not self._players.find_by_lambda(lambda p: p.name == player.name):
                return self._players.push(player)

    def remove_player(self, player_name):
        status, result = self._players.remove_lambda(lambda player: player.name == player_name)
        if status:
            return result
        
        for region in self._regions:
            if region.has_player_name(player_name):
                status = region.remove_player_by_name(player_name)
                self._stats_manager.player_stop(player_name)
                if status and self._players.can_pop():
                    self._on_update(region)
                return status

    def _on_update(self, region):
        same_region = self._players.find_by_lambda(
            lambda player: region.name in player.regions)
        if same_region:
            new_player = same_region[0]
            self._players.remove_lambda(lambda player: player == new_player)

    def add_room(self, player, room_name):
        region = self.most_effective_region_for_room(room_name, player)
        if region:
            return region.add_room(room_name, player)

    def _has_player(self, player):
        for region in self._regions:
            if region.has_player(player):
                return region

        return len(self._players.find_by_lambda(lambda p: p.name == player.name)) > 0

    def _has_region(self, region_name):
        return len(self._regions.find_by_lambda(lambda region: region.name == region_name)) > 0

    def _has_any_region(self, regions):
        for region in regions:
            if self._has_region(region):
                return True
        return False

    def _can_add_player(self, player):
        return not self._has_player(player) and self._has_any_region(player.regions)
