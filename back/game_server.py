import flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from game_manager.simple_game_manager import SimpleGameManager
from game_manager.region import Region
from game_manager.player import Player
import sys

class ResourceWrapper(Resource):
    def __init__(self, manager, parser):
        self._manager = manager
        self._parser = parser


class PlayerResourceWrapper(ResourceWrapper):
    def __init__(self, **kwargs):
        ResourceWrapper.__init__(self, kwargs['manager'], kwargs['parser'])

    def delete(self, player_name):
        if self._manager.remove_player(player_name):
            return self._manager.to_dict(), 200
        else:
            return "Cannot delete player", 400


class PlayersResourceWrapper(ResourceWrapper):
    def __init__(self, **kwargs):
        ResourceWrapper.__init__(self, kwargs['manager'], kwargs['parser'])

    def post(self):
        args = self._parser.parse_args()
        if "player_name" in args and "regions" in args:
            player_name = args.player_name
            regions = args.regions.split(',')
            if self._manager.add_player(Player(name=player_name, regions=regions)):
                return self._manager.to_dict(), 200
            else:
                return "Cannot add player to server", 402
        else:
            return "Post argument player_name and regions are mandatory", 400


class RoomsResourceWrapper(ResourceWrapper):
    def __init__(self, **kwargs):
        ResourceWrapper.__init__(self, kwargs['manager'], kwargs['parser'])

    def post(self):
        args = self._parser.parse_args()
        if "player_name" in args and "regions" in args and "room_name" in args:
            player_name = args.player_name
            regions = args.regions.split(',')
            room_name = args.room_name
            if self._manager.add_room(player=Player(name=player_name, regions=regions),
                                      room_name=room_name):
                return self._manager.to_dict(), 200
        else:
            return "Cannot add room", 400


class GameServer:
    def __init__(self, app, api, manager, parser, api_prefix="/api/v1/"):
        self._app = app
        self._api = api
        self._manager = manager
        self._parser = parser

        self._api.add_resource(RoomsResourceWrapper, f"{api_prefix}rooms",
                               resource_class_kwargs={"manager": self._manager,
                                                      "parser": self._parser})

        self._api.add_resource(PlayersResourceWrapper, f"{api_prefix}players",
                               resource_class_kwargs={"manager": self._manager,
                                                      "parser": self._parser})

        self._api.add_resource(PlayerResourceWrapper, f"{api_prefix}players/<player_name>",
                               resource_class_kwargs={"manager": self._manager,
                                                      "parser": self._parser})

        @app.route(f"{api_prefix}status")
        def status():
            return self._manager.to_dict()

        @app.route(f"{api_prefix}stats")
        def stats():
            return self._manager.stats

    @property
    def app(self):
        return self._app


def init_server():

    app = flask.Flask(__name__)
    CORS(app)
    api = Api(app)

    parser = reqparse.RequestParser()
    parser.add_argument("player_name")
    parser.add_argument("room_name")
    parser.add_argument("regions")

    manager = SimpleGameManager(players_max=100,
                                regions_max=3)

    manager.add_region(Region(name="EUROPA",
                              max_players=100,
                              room_size=4,
                              queue_size=20))

    manager.add_region(Region(name="ASIA",
                              max_players=100,
                              room_size=4,
                              queue_size=20))

    manager.add_region(Region(name="AFRICA",
                              max_players=100,
                              room_size=4,
                              queue_size=20))

    return GameServer(app, api, manager, parser)


def main():
    init_server().app.run(debug=True, host='0.0.0.0')


if __name__ == "__main__":
    main()
