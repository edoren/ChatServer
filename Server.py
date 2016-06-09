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

        self.logged_users = Connect.SafeList()

    def HandleNewConnection(self, socket_manager):
        logger.info("New connection from {}:{}"
                    .format(*socket_manager.address))

    def HandleClientRequest(self, socket_manager):
        msg = socket_manager.Receive()
        if msg is None or not IsValidMessage(msg):
            self.SendResponse(msg.type,
                              ResponseCode.INVALID_MESSAGE,
                              socket_manager)
            return

        if msg.type == MessageType.CHAT:
            self.ProcessChatMessage(msg, socket_manager)
        elif (msg.type == MessageType.LOGIN):
            self.ProcessLoginMessage(msg, socket_manager)
        elif (msg.type == MessageType.REGISTER):
            self.ProcessRegisterMessage(msg, socket_manager)
        elif (msg.type == MessageType.CREATE_ROOM):
            self.ProcessCreateRoomMessage(msg, socket_manager)
        elif (msg.type == MessageType.REMOVE_ROOM):
            self.ProcessRemoveRoomMessage(msg, socket_manager)

    def HandleClientClose(self, socket_manager):
        logger.info("Closed conection {}:{}".format(*socket_manager.address))
        if socket_manager in self.logged_users:
            self.logged_users.remove(socket_manager)

    def HandleServerClose(self):
        msg = Connect.Message(MessageType.SERVER_CLOSE)
        self.ServerBroadcast(msg, self.server.clients)
        logger.info("Server Closed.")

    def ProcessChatMessage(self, msg, socket_manager):
        logger.debug(msg.content.get("message"))
        self.SendResponse(MessageType.CHAT, ResponseCode.OK, socket_manager)
        broadcast = Connect.Message(MessageType.NEW_CHAT, msg.content)
        self.ServerBroadcast(broadcast, self.logged_users)

    def ProcessLoginMessage(self, msg, socket_manager):
        user = self.database.GetUser(msg.content.get("user"))
        if user is None or user.password != msg.content.get("password"):
            self.SendResponse(msg.type,
                              ResponseCode.INVALID_LOGIN_INFO,
                              socket_manager)
        else:
            self.logged_users.append(socket_manager)
            logger.debug("New login from user %s.", user.user)
            self.SendResponse(msg.type, ResponseCode.OK, socket_manager,
                              self.room_manager.GetRoomList())

    def ProcessRegisterMessage(self, msg, socket_manager):
        # Check for an invalid user
        match = re.fullmatch("^[a-zA-Z][a-zA-Z0-9_.]+$",
                             msg.content.get("user"))
        if match is None:
            self.SendResponse(msg.type,
                              ResponseCode.INVALID_USERNAME,
                              socket_manager)

        user = User(**msg.content)

        result = self.database.Insert(user)
        if result:
            logger.debug("New user created with username: %s.", user.user)
            self.SendResponse(msg.type, ResponseCode.OK, socket_manager)
        else:
            self.SendResponse(msg.type,
                              ResponseCode.USER_ALREADY_REGISTERED,
                              socket_manager)

    def ProcessCreateRoomMessage(self, msg, socket_manager):
        room_name = msg.content.get("name")
        user = self.database.GetUser(msg.content.get("owner"))
        if user is not None:
            result = self.room_manager.CreateRoom(room_name, user)
            if result is not None:
                self.SendResponse(msg.type,
                                  ResponseCode.OK,
                                  socket_manager)
                broadcast = Connect.Message(MessageType.NEW_ROOM, msg.content)
                self.ServerBroadcast(broadcast, self.logged_users)
            else:
                self.SendResponse(msg.type,
                                  ResponseCode.ROOM_ALREADY_CREATED,
                                  socket_manager)
        else:
            self.SendResponse(msg.type,
                              ResponseCode.NON_EXISTING_USER,
                              socket_manager)

    def ProcessRemoveRoomMessage(self, msg, socket_manager):
        room_name = msg.content.get("name")
        user = self.database.GetUser(msg.content.get("owner"))
        if user is not None:
            result = self.room_manager.RemoveRoom(room_name, user)
            if result == 0:
                self.SendResponse(msg.type, ResponseCode.OK, socket_manager)
                broadcast = Connect.Message(MessageType.DELETE_ROOM,
                                            {"name": room_name})
                self.ServerBroadcast(broadcast, self.logged_users)
            elif result == 1:
                self.SendResponse(msg.type,
                                  ResponseCode.NON_EXISTING_ROOM,
                                  socket_manager)
            elif result == 2:
                self.SendResponse(msg.type,
                                  ResponseCode.NOT_ROOM_OWNER,
                                  socket_manager)
        else:
            self.SendResponse(msg.type,
                              ResponseCode.NON_EXISTING_USER,
                              socket_manager)

    def SendResponse(self, msg_type, response_code,
                     socket_manager, content=None):
        response_content = {"type": msg_type, "code": response_code,
                            "content": content}
        response = Connect.Message(MessageType.RESPONSE, response_content)
        socket_manager.Send(response)

    def ServerBroadcast(self, msg, users):
        for socket_manager in users:
            try:
                socket_manager.Send(msg)
            except:
                pass
