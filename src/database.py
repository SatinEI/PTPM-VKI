import sqlite3
from pathlib import Path


class RegistrationDatabase:

    def __init__(self, path: str | Path = "registration.sqlite3") -> None:
        self._connection = sqlite3.connect(path)
        with self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS registrations (
                    login TEXT NOT NULL,
                    password TEXT NOT NULL,
                    confirmation TEXT NOT NULL,
                    authorization_result INTEGER NOT NULL CHECK (authorization_result IN (0, 1)),
                    error_message TEXT NOT NULL DEFAULT '',
                    warning_message TEXT NOT NULL DEFAULT '',
                    PRIMARY KEY (login, password, confirmation)
                )
                """
            )

    def add_record(
        self,
        login: str,
        password: str,
        confirmation: str,
        result: tuple[bool, str],
    ) -> None:
        success, message = result
        error_message = "" if success else message
        warning_message = message if success else ""
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO registrations
                    (login, password, confirmation, authorization_result, error_message, warning_message)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (login, password, confirmation, int(success), error_message, warning_message),
            )

    def get_record(
        self, login: str, password: str, confirmation: str
    ) -> tuple[bool, str] | None:
        row = self._connection.execute(
            """
            SELECT authorization_result, error_message, warning_message
            FROM registrations
            WHERE login = ? AND password = ? AND confirmation = ?
            """,
            (login, password, confirmation),
        ).fetchone()
        if row is None:
            return None
        success = bool(row[0])
        return success, row[2] if success else row[1]

    def delete_record(self, login: str, password: str, confirmation: str) -> bool:
        with self._connection:
            cursor = self._connection.execute(
                """
                DELETE FROM registrations
                WHERE login = ? AND password = ? AND confirmation = ?
                """,
                (login, password, confirmation),
            )
        return cursor.rowcount > 0

    def close(self) -> None:
        self._connection.close()
