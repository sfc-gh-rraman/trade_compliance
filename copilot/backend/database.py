import os
from typing import Any, Optional
from contextlib import contextmanager
import snowflake.connector
from snowflake.connector import DictCursor
from config import get_settings


class SnowflakeConnection:
    _instance: Optional["SnowflakeConnection"] = None
    _conn: Optional[snowflake.connector.SnowflakeConnection] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _is_spcs(self) -> bool:
        token_path = "/snowflake/session/token"
        return os.path.exists(token_path) and os.getenv("SNOWFLAKE_HOST") is not None
    
    def _get_token(self) -> str:
        with open("/snowflake/session/token", "r") as f:
            return f.read().strip()
    
    def _create_connection(self) -> snowflake.connector.SnowflakeConnection:
        settings = get_settings()
        
        if self._is_spcs():
            return snowflake.connector.connect(
                host=os.getenv("SNOWFLAKE_HOST"),
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                token=self._get_token(),
                authenticator="oauth",
                database=settings.snowflake_database,
                schema=settings.snowflake_schema,
                warehouse=settings.snowflake_warehouse,
            )
        else:
            return snowflake.connector.connect(
                connection_name=os.getenv("SNOWFLAKE_CONNECTION_NAME") or settings.snowflake_connection_name,
                database=settings.snowflake_database,
                schema=settings.snowflake_schema,
                warehouse=settings.snowflake_warehouse,
            )
    
    def get_connection(self) -> snowflake.connector.SnowflakeConnection:
        if self._conn is None or self._conn.is_closed():
            self._conn = self._create_connection()
        return self._conn
    
    def reconnect(self) -> snowflake.connector.SnowflakeConnection:
        if self._conn and not self._conn.is_closed():
            self._conn.close()
        self._conn = self._create_connection()
        return self._conn
    
    def close(self):
        if self._conn and not self._conn.is_closed():
            self._conn.close()
            self._conn = None


def get_db() -> SnowflakeConnection:
    return SnowflakeConnection()


@contextmanager
def get_cursor(dict_cursor: bool = True):
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor(DictCursor) if dict_cursor else conn.cursor()
    try:
        yield cursor
    except snowflake.connector.errors.ProgrammingError as e:
        if e.errno == 390114:
            conn = db.reconnect()
            cursor = conn.cursor(DictCursor) if dict_cursor else conn.cursor()
            yield cursor
        else:
            raise
    finally:
        cursor.close()


def execute_query(sql: str, params: Optional[dict] = None) -> list[dict[str, Any]]:
    with get_cursor() as cursor:
        cursor.execute(sql, params or {})
        return cursor.fetchall()


def execute_query_single(sql: str, params: Optional[dict] = None) -> Optional[dict[str, Any]]:
    with get_cursor() as cursor:
        cursor.execute(sql, params or {})
        return cursor.fetchone()


async def execute_query_async(sql: str, params: Optional[dict] = None) -> list[dict[str, Any]]:
    return execute_query(sql, params)
