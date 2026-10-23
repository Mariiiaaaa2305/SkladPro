
from app.extensions import get_db_connection
from app.models.user import User


class UserRepository:
    ALLOWED_ROLES = ("admin", "manager")

    def get_by_username(self, username):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id, username, password_hash, role,
                       created_at, is_active
                FROM users
                WHERE username = %s
                """,
                (username,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                role=row["role"],
                created_at=row["created_at"],
                is_active=row["is_active"],
            )
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def create(self, username, password, role="manager"):
        username = username.strip() if isinstance(username, str) else ""

        if len(username) < 3 or len(username) > 80:
            raise ValueError("Логін має містити від 3 до 80 символів.")

        if not isinstance(password, str) or len(password) < 8:
            raise ValueError("Пароль має містити щонайменше 8 символів.")

        if role not in self.ALLOWED_ROLES:
            raise ValueError("Невідома роль користувача.")

        password_hash = User.hash_password(password)
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, %s)
                """,
                (username, password_hash, role),
            )
            connection.commit()
            return cursor.lastrowid
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def get_all(self):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id, username, role, created_at, is_active
                FROM users
                ORDER BY id ASC
                """
            )
            return cursor.fetchall()
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def count_admins(self):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM users
                WHERE role = 'admin' AND is_active = TRUE
                """
            )
            return cursor.fetchone()["total"]
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def update_role(self, user_id, role):
        if role not in self.ALLOWED_ROLES:
            raise ValueError("Невідома роль користувача.")

        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE users
                SET role = %s
                WHERE id = %s
                """,
                (role, user_id),
            )
            connection.commit()
            return cursor.rowcount > 0
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def set_active(self, user_id, is_active):
        if not isinstance(is_active, bool):
            raise ValueError("Некоректний статус облікового запису.")

        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE users
                SET is_active = %s
                WHERE id = %s
                """,
                (is_active, user_id),
            )
            connection.commit()
            return cursor.rowcount > 0
        except Exception:
            connection.rollback()
            raise
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
