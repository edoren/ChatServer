import Connect
from enum import IntEnum


class MessageType(IntEnum):
    CHAT = 0
    LOGIN = 1
    REGISTER = 2
    CREATE_ROOM = 3
    REMOVE_ROOM = 4

    RESPONSE = 100

    NEW_ROOM = 110
    NEW_CHAT = 111
    DELETE_ROOM = 112

    SERVER_CLOSE = 200


class ResponseCode(IntEnum):
    OK = 0
    INVALID_MESSAGE = 1
    INVALID_USERNAME = 2
    INVALID_LOGIN_INFO = 3
    USER_ALREADY_REGISTERED = 4
    ROOM_ALREADY_CREATED = 5
    NON_EXISTING_USER = 6
    NON_EXISTING_ROOM = 7
    NOT_ROOM_OWNER = 8


def IsValidMessage(msg):
    if not isinstance(msg, Connect.Message):
        return False

    content = []

    if msg.type == MessageType.CHAT:
        content = ["user", "room", "message"]
    elif msg.type == MessageType.LOGIN:
        content = ["user", "password"]
    elif msg.type == MessageType.REGISTER:
        content = ["name", "last_name", "user", "password", "age", "gender"]
    elif msg.type == MessageType.CREATE_ROOM:
        content = ["name", "owner"]
    elif msg.type == MessageType.REMOVE_ROOM:
        content = ["name", "owner"]

    if len(content) == 0:
        return False

    for c in content:
        if c not in msg.content:
            return False

    return True
