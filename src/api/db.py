import sqlite3
from queue import Queue
from threading import Thread
from typing import NoReturn, Callable, Optional, Tuple, List

from . import utils
from .models.company import Company
from .models.company_data import CompanyData
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


CommittedCallbackType = Optional[Callable[[int, int, Optional[List]], None]]
RowType = Tuple[int, str, str, float, float, float, float, float, float, float, float, float, float]


class AsyncDB:
    def __init__(self):
        self.transaction_queue = Queue()
        self.callback_queue = Queue()
        self.worker = Thread(target=self._commit_transactions_thread)
        self.connection = None
        self.count_added = 0
        self.count_committed = 0
        self.worker.start()

    def commit(self,
               transaction: Tuple[str, Optional[Tuple]],
               callback: CommittedCallbackType):
        self.transaction_queue.put(transaction)
        self.callback_queue.put(callback)
        self.count_added += 1

    def commit_many(self,
                    transaction: Tuple[str, Optional[List[Tuple]]],
                    callback: CommittedCallbackType):
        self.transaction_queue.put(transaction)
        self.callback_queue.put(callback)
        self.count_added += 1

    def shutdown(self):
        self.transaction_queue.put(None)

    def _commit_transactions_thread(self):
        if self.connection is None:
            self.connection = get_connection()
        while True:
            transaction = self.transaction_queue.get()

            if transaction is None:
                close_connection(self.connection)
                self.connection = None
                break

            callback = self.callback_queue.get()

            cursor = self.connection.cursor()
            query, args = transaction

            if type(args) == list:
                cursor.executemany(query, args)
            else:
                args = () if args is None else args
                cursor.execute(query, args)

            self.connection.commit()
            result = cursor.fetchall()

            if len(result) == 0:
                result = None

            self.count_committed += 1

            if callback is not None:
                callback(self.count_committed, self.count_added, result)

    @staticmethod
    def get_instance():
        if not hasattr(AsyncDB, '_instance'):
            AsyncDB._instance = AsyncDB()
        return AsyncDB._instance

    def __del__(self):
        self.transaction_queue.join()
        if self.connection is not None:
            close_connection(self.connection)


class DBCompanyManager:

    @staticmethod
    def add(company: Company, callback: CommittedCallbackType) -> NoReturn:
        query = "INSERT OR IGNORE INTO companies (company_id, company_name) VALUES (?, ?)"
        args = (company.index, company.name)
        AsyncDB.get_instance().commit((query, args), callback)

    @staticmethod
    def remove(company: Company, callback: CommittedCallbackType) -> NoReturn:
        query = "DELETE FROM companies WHERE company_id = ?"
        args = (company.index,)
        AsyncDB.get_instance().commit((query, args), callback)

    @staticmethod
    def update(company: Company, callback: CommittedCallbackType) -> NoReturn:
        query = "UPDATE companies SET company_name = ? WHERE company_id = ?"
        args = (company.name, company.index)
        AsyncDB.get_instance().commit((query, args), callback)

    @staticmethod
    def get_all(callback: CommittedCallbackType) -> NoReturn:
        query = "SELECT * FROM companies"
        AsyncDB.get_instance().commit((query, None), callback)

    @staticmethod
    def get(company_id: int, callback: CommittedCallbackType) -> NoReturn:
        query = "SELECT * FROM companies WHERE company_id = ?"
        args = (company_id,)
        AsyncDB.get_instance().commit((query, args), callback)


class DBCompanyDataManager:

    @staticmethod
    def add(company_data: CompanyData, callback: CommittedCallbackType, separately=False) -> NoReturn:
        query = """INSERT OR IGNORE INTO reports 
        (company_id, period, string_code, col_0, col_1, col_2, col_3, col_4, col_5, col_6, col_7, col_8, col_9) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        args = (company_data.company.index, company_data.year)
        batch_args = []
        for c_id, c_row in company_data:
            row_args = args
            row_args += (int(c_id),)
            row_args += tuple(c_row.tolist())
            batch_args.append(row_args)
        if separately:
            for separate_args in batch_args:
                AsyncDB.get_instance().commit((query, separate_args), callback)
        else:
            AsyncDB.get_instance().commit_many((query, batch_args), callback)

    @staticmethod
    def remove(company_data: CompanyData, callback: CommittedCallbackType) -> NoReturn:
        query = "DELETE FROM reports WHERE company_id = ? AND period = ?"
        args = (company_data.company.index, company_data.year)
        AsyncDB.get_instance().commit((query, args), callback)

    @staticmethod
    def update(company_data: CompanyData, callback: CommittedCallbackType, commit_separately=False) -> NoReturn:
        query = """UPDATE reports
        SET company_id = ?, period = ?, string_code = ?,
         col_0 = ?, col_1 = ?, col_2 = ?, col_3 = ?, col_4 = ?, col_5 = ?, col_6 = ?, col_7 = ?, col_8 = ?, col_9 = ?
        WHERE company_id = ? AND period = ? AND string_code = ?"""

        args = (company_data.company.index, company_data.year, company_data)
        batch_args = [args + row[0] + tuple(row[1]) for row in company_data]
        if commit_separately:
            for separate_args in batch_args:
                AsyncDB.get_instance().commit((query, separate_args), callback)
        else:
            AsyncDB.get_instance().commit_many((query, batch_args), callback)

    @staticmethod
    def add_row(row: RowType, callback: CommittedCallbackType) -> NoReturn:
        row_query = """INSERT OR IGNORE INTO reports 
        (company_id, period, string_code, col_0, col_1, col_2, col_3, col_4, col_5, col_6, col_7, col_8, col_9) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        AsyncDB.get_instance().commit((row_query, row), callback)

    @staticmethod
    def update_row(row: RowType, callback: CommittedCallbackType) -> NoReturn:
        pass

    @staticmethod
    def remove_row(row: RowType, callback: CommittedCallbackType) -> NoReturn:
        pass

    @staticmethod
    def get_row(row: RowType, callback: CommittedCallbackType) -> NoReturn:
        pass

    @staticmethod
    def get_all(callback: CommittedCallbackType) -> NoReturn:
        pass

    @staticmethod
    def get(company: Company, callback: CommittedCallbackType) -> NoReturn:
        pass


class DBPeriodManager:
    @staticmethod
    def add(year: str, callback: CommittedCallbackType) -> NoReturn:
        query = "INSERT OR IGNORE INTO `available_periods` (year) VALUES (?)"
        args = (year,)
        AsyncDB.get_instance().commit((query, args), callback)

    @staticmethod
    def remove(year: str, callback: CommittedCallbackType) -> NoReturn:
        query = "DELETE FROM `available_periods` WHERE year = ?"
        args = (year,)
        AsyncDB.get_instance().commit((query, args), callback)

    @staticmethod
    def is_period_available_sync(year: str) -> bool:
        """
        Checks whether specified year exists in downloaded years table (blocking!)

        :param year: year to check
        """
        query = "SELECT DISTINCT COUNT() FROM `available_periods` WHERE year = ?"
        args = (year,)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
        result = cursor.fetchone()[0] > 0
        cursor.close()
        close_connection(conn)
        return result

    @staticmethod
    def get_all(callback: CommittedCallbackType) -> NoReturn:
        query = "SELECT * FROM available_periods"
        args = None
        AsyncDB.get_instance().commit((query, args), callback)
