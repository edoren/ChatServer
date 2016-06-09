import Connect
import socket
import argparse

from Server import ChatServerHandler
from Serializer import BsonSerializer


def IsValidIPv4(address):
    if address == "localhost":
        return True
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False
    return True


parser = argparse.ArgumentParser(description="EdoChat Server.")

parser.add_argument(
    "host",
    type=str,
    default="localhost",
    help="the server ip",
    metavar="host",
    nargs="?"
)

parser.add_argument(
    "port",
    type=int,
    default=9999,
    help="the server port",
    metavar="port",
    nargs="?"
)

args = parser.parse_args()


if __name__ == "__main__":

    if not IsValidIPv4(args.host):
        print("Invalid host IPv4 address.")
        parser.print_usage()
        exit()

    s = Connect.TCPServer(
        (args.host, args.port),
        ChatServerHandler,
        BsonSerializer
    )

    try:
        s.Start()
    except KeyboardInterrupt:
        pass
