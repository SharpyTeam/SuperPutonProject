import sqlite3
from queue import Queue
from threading import Thread
from typing import NoReturn, Callable, Optional, Tuple, List

from . import utils
from .. import config


def create_db() -> NoReturn:
    open(utils.get_db_path(), 'a').close()
    db = sqlite3.connect(utils.get_db_path())
    schema_file = open(utils.get_schema_path(), 'r')
    sql = schema_file.read()
    schema_file.close()
    db.executescript(sql)
    db.close()


def get_connection() -> NoReturn:
    return sqlite3.connect(utils.get_db_path(), config.DB_LOCK_TIMEOUT)


def close_connection(conn: sqlite3.Connection):
    conn.commit()  # Ensure that all transactions were applied
    conn.close()


class AsyncDB:
    def __init__(self):
        self.transaction_queue = Queue()
        self.callback_queue = Queue()
        self.worker = Thread(target=self.commit_transactions_thread)
        self.connection = get_connection()

    def commit(self,
               transaction: Tuple[str, Tuple],
               callback: Optional[Callable[[int, int, Optional[List]], None]]):
        self.transaction_queue.put(transaction)
        self.callback_queue.put(callback)

    def commit_transactions_thread(self):
        while True:
            transaction = self.transaction_queue.get()
            callback = self.callback_queue.get()

            if transaction is None:
                close_connection(self.connection)
                break

            query, args = transaction
            cursor = self.connection.cursor()
            cursor.execute(query, args)
            self.connection.commit()
            result = cursor.fetchall()

            if len(result) == 0:
                result = None

            if callback is not None:
                callback(result)
