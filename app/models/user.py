
from werkzeug.security import check_password_hash, generate_password_hash


class User:
    def __init__(
        self,
        id,
        username,
        password_hash,
        role,
        created_at=None,
        is_active=True,
    ):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at
        self.is_active = bool(is_active)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_employee(self):
        return self.role == "manager"
