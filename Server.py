import re

import Connect

import Logger
from MessageCodes import MessageType, ResponseCode, IsValidMessage
from DBManager import DBManager
from RoomManager import RoomManager
from DataModel import User


# Load the Server logging.Logger instance
logger = Logger.GetLogger(__name__)


# Server handler, here goes all the server main process
class ChatServerHandler(Connect.BaseServerHandler):

    def HandleServerStart(self):
        # Connect to the MongoDB
        self.database = DBManager(host="localhost",
                                  port=27017,
                                  testing=True)

        address = self.server.address
        logger.info("Server started in address %s:%d", *address)

        self.admin_user = User(name="admin", user="_admin")

        self.room_manager = RoomManager()
        self.room_manager.CreateRoom("default", self.admin_user)

    def HandleNewConnection(self, socket_manager):
        logger.info("Client new connection.")

    def HandleClientRequest(self, socket_manager):
        msg = socket_manager.Receive()
        if msg is None:
            return  # Bad message - Ignore

        status = self.ProcessMessage(msg)

        response_content = {"message_id": msg.type, "status": status}
        response = Connect.Message(MessageType.RESPONSE, response_content)
        socket_manager.Send(response)

    def HandleClientClose(self, socket_manager):
        logger.info("Client disconnected.")
        msg = Connect.Message(MessageType.CHAT, "Chau!")
        socket_manager.Send(msg)

    def HandleServerClose(self):
        msg = Connect.Message(MessageType.SERVER_CLOSE)
        self.ServerBroadcast(msg)
        logger.info("Server Closed.")

    def ProcessMessage(self, msg):
        if not IsValidMessage(msg):
            return ResponseCode.INVALID_MESSAGE

        if msg.type == MessageType.CHAT:
            logger.info(msg)

        elif (msg.type == MessageType.LOGIN):
            user = self.database.GetUser(msg.content.get("user"))
            if user is None or user.password != msg.content.get("password"):
                return ResponseCode.INVALID_LOGIN_INFO
            else:
                logger.debug("New login from user %s.", user.user)
                return ResponseCode.OK

        elif (msg.type == MessageType.REGISTER):
            # Check for an invalid user
            match = re.fullmatch("^[a-zA-Z][a-zA-Z0-9\_\.]+$",
                                 msg.content.get("user"))
            if match is None:
                return ResponseCode.INVALID_USERNAME

            user = User(**msg.content)

            result = self.database.Insert(user)
            if result:
                return ResponseCode.OK
            else:
                return ResponseCode.USER_ALREADY_REGISTERED

        elif (msg.type == MessageType.CREATE_ROOM):
            room_name = msg.content.get("name")
            user = self.database.GetUser(msg.content.get("owner"))
            if user is not None:
                result = self.room_manager.CreateRoom(room_name, user)
                if result == 0:
                    return ResponseCode.OK
                else:
                    return ResponseCode.ROOM_ALREADY_CREATED
            else:
                return ResponseCode.NON_EXISTING_USER

        elif (msg.type == MessageType.REMOVE_ROOM):
            room_name = msg.content.get("name")
            user = self.database.GetUser(msg.content.get("owner"))
            if user is not None:
                result = self.room_manager.RemoveRoom(room_name, user)
                if result == 0:
                    return ResponseCode.OK
                elif result == 1:
                    return ResponseCode.NON_EXISTING_ROOM
                elif result == 2:
                    return ResponseCode.NOT_ROOM_OWNER
            else:
                return ResponseCode.NON_EXISTING_USER

    def ServerBroadcast(self, msg):
        for socket_manager in self.server.clients:
            try:
                socket_manager.Send(msg)
            except:
                pass
