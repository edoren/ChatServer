import bson

import Connect


# Bson serializer to use in the server messages
class BsonSerializer(Connect.MessageSerializer):
    def Encode(obj):
        try:
            return bson.BSON.encode(obj)
        except:
            return None

    def Decode(data):
        try:
            return bson.BSON.decode(data)
        except:
            return None
