import Connect

from Server import ChatServerHandler
from Serializer import BsonSerializer


if __name__ == "__main__":

    s = Connect.TCPServer(
        ("localhost", 9999),
        ChatServerHandler,
        BsonSerializer
    )

    try:
        s.Start()
    except KeyboardInterrupt:
        pass
