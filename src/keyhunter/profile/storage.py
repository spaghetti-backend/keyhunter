import sqlite3
from contextlib import contextmanager
from typing import Iterator

from platformdirs import user_data_path

from keyhunter import const as CONST


class SQLite3Storage:
    def __init__(self) -> None:
        self._db_path = (
            user_data_path(CONST.APP_NAME, ensure_exists=True)
            / CONST.TYPING_SESSIONS_STORAGE_NAME
        )

        self._create_tables()

    @contextmanager
    def _db_connection(self) -> Iterator[sqlite3.Connection]:
        conn = None
        try:
            conn = sqlite3.connect(
                database=self._db_path,
            )
            yield conn
            conn.commit()
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def add_session_summary(
        self, session_summary: dict, keystrokes_summary: list[dict]
    ) -> None:
        typing_session_stmt = """
        INSERT INTO
        typing_session (
          total_chars, correct_chars, speed, accuracy, elapsed_time_ms)
        VALUES (
          :total_chars, :correct_chars, :speed, :accuracy, :elapsed_time_ms)
        RETURNING id
        """
        keystrokes_summary_stmt = """
        INSERT INTO
        keystroke (
          typing_session_id, char, total, correct, accuracy, speed, elapsed_time_ms)
        VALUES (
          :typing_session_id, :char, :total, :correct, :accuracy, :speed, :elapsed_time_ms)
        """

        with self._db_connection() as conn:
            typing_session_id = conn.execute(
                typing_session_stmt, session_summary
            ).fetchone()

            for keystroke_summary in keystrokes_summary:
                keystroke_summary[CONST.TYPING_SESSION_ID_KEY] = typing_session_id[0]

            conn.executemany(keystrokes_summary_stmt, keystrokes_summary)

    def load_last_session_summary(self) -> tuple[int, int, int]:
        stmt = """
        SELECT
          speed, accuracy, elapsed_time_ms
        FROM typing_session
        ORDER BY id DESC LIMIT 1
        """

        with self._db_connection() as conn:
            return conn.execute(stmt).fetchone()

    def load_sessions_summary(
        self, today_only: bool
    ) -> tuple[int, int, int, int, int, int]:
        stmt = f"""
        SELECT
          count(*),
          cast(round(avg(speed)) as INTEGER),
          max(speed),
          cast(round(avg(accuracy)) as INTEGER),
          max(accuracy),
          sum(elapsed_time_ms)
        FROM typing_session
        {"WHERE DATE(date, 'localtime') = DATE('now', 'localtime')" if today_only else ""}
        """

        with self._db_connection() as conn:
            return conn.execute(stmt).fetchone()

    def _create_tables(self) -> None:
        stmt = """
        CREATE TABLE IF NOT EXISTS
        typing_session (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          total_chars INTEGER,
          correct_chars INTEGER,
          speed INTEGER,
          accuracy INTEGER,
          elapsed_time_ms INTEGER,
          date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_typing_session_date ON typing_session(date);

        CREATE TABLE IF NOT EXISTS
        keystroke (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          typing_session_id INTEGER,
          char TEXT,
          total INTEGER,
          correct INTEGER,
          accuracy INTEGER,
          speed INTEGER,
          elapsed_time_ms INTEGER,
          FOREIGN KEY (typing_session_id) REFERENCES typing_session(id) ON DELETE RESTRICT
        );

        CREATE INDEX IF NOT EXISTS idx_keystroke_char ON keystroke(char);
        """
        with self._db_connection() as conn:
            conn.executescript(stmt)
