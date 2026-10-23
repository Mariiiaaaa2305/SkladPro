
from app.extensions import get_db_connection
from app.models.notification import Notification


class NotificationRepository:
    """Репозиторій для роботи зі сповіщеннями."""

    def create(self, product_id, message):
        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO notifications (product_id, message)
                VALUES (%s, %s)
                """,
                (product_id, message),
            )

            notification_id = cursor.lastrowid
            connection.commit()
            return notification_id

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def get_all(self, unread_only=False, limit=100):
        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or not 1 <= limit <= 1000
        ):
            raise ValueError("Ліміт має бути від 1 до 1000.")

        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT
                    n.id,
                    n.product_id,
                    p.name AS product_name,
                    n.message,
                    n.is_read,
                    n.created_at
                FROM notifications n
                JOIN products p ON p.id = n.product_id
            """

            if unread_only:
                query += " WHERE n.is_read = FALSE"

            query += " ORDER BY n.created_at DESC, n.id DESC LIMIT %s"
            cursor.execute(query, (limit,))

            rows = cursor.fetchall()
            result = []

            for row in rows:
                notification = Notification.from_dict({
                    "id": row["id"],
                    "product_id": row["product_id"],
                    "message": row["message"],
                    "is_read": row["is_read"],
                    "created_at": row["created_at"],
                }).to_dict()

                notification["product_name"] = row["product_name"]
                result.append(notification)

            return result

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def mark_as_read(self, notification_id):
        if (
            not isinstance(notification_id, int)
            or isinstance(notification_id, bool)
            or notification_id <= 0
        ):
            raise ValueError("Некоректний ID сповіщення.")

        connection = get_db_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE notifications
                SET is_read = TRUE
                WHERE id = %s
                """,
                (notification_id,),
            )

            updated = cursor.rowcount > 0
            connection.commit()
            return updated

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
