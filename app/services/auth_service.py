
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()

    def login(self, username, password):
        if not isinstance(username, str) or not isinstance(password, str):
            return None

        username = username.strip()

        if not username or not password:
            return None

        user = self.user_repository.get_by_username(username)

        if user is None:
            return None

        if not user.is_active:
            return None

        if not user.check_password(password):
            return None

        return user
