import Connect

import Logger
from DataModel import User


# Load the Server logging.Logger instance
logger = Logger.GetLogger(__name__)


class Room:
    def __init__(self, name, owner):
        if not isinstance(owner, User):
            raise TypeError("owner must be an instance of {}"
                            .format(User.__class__))

        self.name = name
        self.owner = owner

        # Dict of User and a list of socket_managers {user: [socket_manager]}
        self.users = Connect.SafeDict()

    def AddUser(self, user, socket_manager):
        if not isinstance(user, User):
            raise TypeError("user must be an instance of {}"
                            .format(User.__class__))
        if not isinstance(socket_manager, Connect.SocketManager):
            raise TypeError("socket_manager must be an instance of {}"
                            .format(Connect.SocketManager.__class__))
        if self.users.get(user) is None:
            self.users[user] = [socket_manager]
        else:
            self.users[user].append(socket_manager)

    def RemoveUser(self, user, socket_manager):
        if not isinstance(user, User):
            raise TypeError("user must be an instance of {}"
                            .format(User.__class__))
        if not isinstance(socket_manager, Connect.SocketManager):
            raise TypeError("socket_manager must be an instance of {}"
                            .format(Connect.SocketManager.__class__))
        self.users.pop(user, None)

    def Broadcast(self, msg):
        if not isinstance(msg, Connect.Message):
            raise TypeError("msg must be an instance of {}"
                            .format(Connect.Message.__class__))

        for user, socket_list in self.users.items():
            for socket_manager in socket_list:
                socket_manager.Send(msg)


class RoomManager:
    def __init__(self):
        self.rooms = Connect.SafeDict()

    def CreateRoom(self, name, owner):
        if name not in self.rooms:
            self.rooms[name] = Room(name, owner)
            logger.info("Room '%s' created with owner '%s'",
                        name, owner.user)
            return self.rooms[name]
        else:
            logger.error("User '%s' tryied to create an existent Room '%s'",
                         owner.user, name)
            return None  # Room name already in use

    def RemoveRoom(self, name, owner):
        if name in self.rooms:
            if self.rooms[name].owner == owner:
                del self.rooms[name]
                logger.info("Room '%s' deleted", name)
                return 0
            else:
                logger.error("User '%s' tried to remove a not owned Room '%s'",
                             owner.user, name)
                return 2  # User try to remove a not owned Room
        else:
            return 1  # Room doesn't exist

    def GetRoomList(self):
        ret = []
        for room in self.rooms.values():
            if room.name != "default":
                ret.append({"name": room.name, "owner": room.owner.user})
        return ret
