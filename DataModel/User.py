__all__ = ["User"]


class User:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.last_name = kwargs.get("last_name")
        self.user = kwargs.get("user")
        self.password = kwargs.get("password")
        self.age = kwargs.get("age")
        self.gender = kwargs.get("gender")

    def __hash__(self):
        return hash(self.user)

    def __eq__(self, other):
        return self.user == other.user

    def __ne__(self, other):
        return self.user != other.user
