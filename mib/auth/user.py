from flask_login import UserMixin


class User(UserMixin):
    """
    This class represents an authenticated user.
    It is not a model, it is only a lightweight class used
    to represents an authenticated user.
    """

    id = None
    email = None
    is_active = None
    is_admin = None
    is_anonymous = False
    extra_data = None

    @staticmethod
    def build_from_json(json: dict):
        kw = {
            key: json[key]
            for key in ["id", "email", "firstname", "lastname", "is_active"]
        }
        extra = json.copy()
        all(map(extra.pop, kw))
        kw["extra"] = extra

        return User(**kw)

    def __init__(self, **kw):
        if kw is None:
            raise RuntimeError("You can't build the user with none dict")
        self.id = kw["id"]
        self.email = kw["email"]
        self.is_active = kw["is_active"]
        self.firstname = kw["firstname"]
        self.lastname = kw["lastname"]
        self.extra_data = kw["extra"]
        self._authenticated = False

    def get_id(self):
        return self.id

    @property
    def is_authenticated(self):
        return self._authenticated

    def authenticate(self):
        self._authenticated = True

    def __getattr__(self, item):
        if item in self.__dict__:
            return self[item]
        elif item in self.extra_data:
            return self.extra_data[item]
        else:
            raise AttributeError("Attribute %s does not exist" % item)

    def __str__(self):
        s = "User Object\n"
        for (key, value) in self.__dict__.items():
            s += "%s=%s\n" % (key, value)
        return s
