import sqlite3
import os.path as path
import random
from queue import Queue
from threading import Thread, get_ident
from typing import NoReturn, Callable, Optional, Tuple, List, Union

from . import utils
from .models.company import Company
from .models.company_data import CompanyData
from . import config


class DBManager:
    def __init__(self):
        if not path.exists(utils.get_db_path()):
            open(utils.get_db_path(), 'a').close()
            db = sqlite3.connect(utils.get_db_path())
            schema_file = open(utils.get_schema_path(), 'r')
            sql = schema_file.read()
            schema_file.close()
            db.executescript(sql)
            db.close()
        self.connection_async = None
        self.connections_sync = {}
        self.transactions_queue = Queue()
        self.worker = Thread(target=self._commit_transactions_thread)
        self.started = False

    def _open_connection_sync(self):
        while len(self.connections_sync) > 10:
            self._close_connection_sync(random.choice(list(self.connections_sync.keys())))
        ident = get_ident()
        if ident not in self.connections_sync:
            connection = sqlite3.connect(utils.get_db_path(), config.DB_LOCK_TIMEOUT)
            self.connections_sync[ident] = connection
        return self.connections_sync[ident]

    def _open_connection_async(self):
        if self.connection_async is None:
            self.connection_async = sqlite3.connect(utils.get_db_path(), config.DB_LOCK_TIMEOUT)

    def _close_connection_sync(self, ident):
        if ident in self.connections_sync:
            self.connections_sync[ident].commit()
            self.connections_sync[ident].close()
            del self.connections_sync[ident]

    def _close_connection_async(self):
        if self.connection_async is not None:
            self.connection_async.commit()
            self.connection_async.close()

    def start(self):
        if self.started:
            return
        self._open_connection_sync()
        self.worker.start()
        self.started = True

    def stop(self, join=True):
        if not self.started:
            return
        while len(self.connections_sync) > 0:
            self._close_connection_sync(random.choice(list(self.connections_sync.keys())))
        self.transactions_queue.put(None)
        self.started = False
        if join:
            self.join()

    def join(self):
        self.worker.join()

    def commit_async(self,
                     transaction: Tuple[str, Optional[Tuple]],
                     callback: Optional[Callable[[Optional[List]], None]] = None):
        self.transactions_queue.put((transaction, callback))

    def commit_many_async(self,
                          transaction: Tuple[str, Optional[List[Tuple]]],
                          callback: Optional[Callable[[Optional[List]], None]] = None):
        self.transactions_queue.put((transaction, callback))

    def commit(self, transaction: Tuple[str, Optional[Tuple]]) -> Optional[List]:
        connection = self._open_connection_sync()
        cursor = connection.cursor()
        query, args = transaction
        args = () if args is None else args
        cursor.execute(query, args)
        connection.commit()
        result = cursor.fetchall()
        return result

    def commit_many(self, transaction: Tuple[str, Optional[List[Tuple]]]) -> Optional[List]:
        connection = self._open_connection_sync()
        cursor = connection.cursor()
        query, args = transaction
        cursor.executemany(query, args)
        connection.commit()
        result = cursor.fetchall()
        return result

    def _commit_transactions_thread(self):
        self._open_connection_async()
        while True:
            transaction_data = self.transactions_queue.get()

            if transaction_data is None:
                self._close_connection_async()
                break

            transaction, callback = transaction_data

            cursor = self.connection_async.cursor()
            query, args = transaction

            if type(args) == list:
                cursor.executemany(query, args)
            else:
                args = () if args is None else args
                cursor.execute(query, args)

            self.connection_async.commit()
            result = cursor.fetchall()

            if callback is not None:
                callback(result)

    def __del__(self):
        self.stop()


class DBWrapper(DBManager):
    def __init__(self):
        super().__init__()

    def add_company_async(self, company: Union[Company, List[Company]],
                          callback: Optional[Callable[[], None]] = None) -> NoReturn:
        query = "INSERT OR IGNORE INTO companies (company_id, company_name) VALUES (?, ?)"
        companies = [company] if isinstance(company, Company) else company
        batch_args = []
        for c in companies:
            batch_args.append((c.id, c.name))
        super().commit_many_async((query, batch_args), lambda _: self._add_company_data_async(
            [cd for c in companies for cd in c.data.values()], lambda: callback() if callback is not None else None
        ))

    def remove_company_async(self, company: Union[Company, List[Company]],
                             callback: Optional[Callable[[], None]]) -> NoReturn:
        query = "DELETE FROM companies WHERE company_id = ?"
        companies = [company] if isinstance(company, Company) else company
        batch_args = []
        for c in companies:
            batch_args.append((c.id,))
        super().commit_many_async((query, batch_args), lambda _: self._remove_company_data_async(
            [cd for c in companies for cd in c.data.values()], lambda: callback() if callback is not None else None
        ))

    def update_company_async(self, company: Union[Company, List[Company]],
                             callback: Optional[Callable[[], None]] = None) -> NoReturn:
        query = "UPDATE companies SET company_name = ? WHERE company_id = ?"
        companies = [company] if isinstance(company, Company) else company
        batch_args = []
        for c in companies:
            batch_args.append((c.name, c.id))
        super().commit_many_async((query, batch_args), lambda _: self._update_company_data_async(
            [cd for c in companies for cd in c.data.values()], lambda: callback() if callback is not None else None
        ))

    def get_company_async(self, company_id: int,
                          callback: Optional[Callable[[Optional[Company]], None]] = None) -> NoReturn:
        query = "SELECT * FROM companies WHERE company_id = ?"
        args = (company_id,)

        def f(rows):
            company = Company(rows[0][0], rows[0][1], self)
            self._get_company_data_async(
                company, None,
                lambda: callback(company) if callback is not None else None
            ) if len(rows) == 1 else callback(None) if callback is not None else None

        super().commit_async((query, args), f)

    def get_all_companies_async(self, callback: Optional[Callable[[List[Company]], None]] = None) -> NoReturn:
        query = "SELECT * FROM companies"

        def cb(rows):
            companies = [Company(row[0], row[1], self) for row in rows]
            remaining = [len(companies)]

            def dec():
                remaining[0] -= 1
                if remaining[0] == 0:
                    if callback is not None:
                        callback(companies)

            for company in companies:
                self._get_company_data_async(company, None, dec)

        super().commit_async((query, None), cb)

    def get_all_companies_names_async(self, callback: Optional[Callable[[List[Company]], None]] = None) -> NoReturn:
        query = "SELECT * FROM companies"

        def cb(rows):
            companies = [Company(row[0], row[1], self) for row in rows]
            if callback is not None:
                callback(companies)

        super().commit_async((query, None), cb)

    def _add_company_data_async(self, company_data: Union[CompanyData, List[CompanyData]],
                                callback: Optional[Callable[[], None]] = None,
                                separately=False) -> NoReturn:
        query = """INSERT OR IGNORE INTO reports 
        (company_id, period, string_code, col_0, col_1, col_2, col_3, col_4, col_5, col_6, col_7, col_8, col_9) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        if isinstance(company_data, CompanyData):
            company_data = [company_data]

        batch_args = []
        for cd in company_data:
            for row_index, row in cd:
                row_args = (cd.company.id, cd.year, int(row_index))
                row_args += tuple(row)
                batch_args.append(row_args)
        if separately:
            for separate_args in batch_args:
                super().commit_async((query, separate_args), lambda _: callback() if callback is not None else None)
        else:
            super().commit_many_async((query, batch_args), lambda _: callback() if callback is not None else None)

    def _remove_company_data_async(self, company_data: Union[CompanyData, List[CompanyData]],
                                   callback: Optional[Callable[[], None]] = None) -> NoReturn:
        query = "DELETE FROM reports WHERE company_id = ? AND period = ?"
        if isinstance(company_data, CompanyData):
            company_data = [company_data]
        batch_args = []
        for cd in company_data:
            batch_args.append((cd.company.id, cd.year))
        super().commit_many_async((query, batch_args), lambda _: callback() if callback is not None else None)

    def _update_company_data_async(self, company_data: Union[CompanyData, List[CompanyData]],
                                   callback: Optional[Callable[[], None]] = None, separately=False) -> NoReturn:
        query = """UPDATE reports
        SET
         col_0 = ?, col_1 = ?, col_2 = ?, col_3 = ?, col_4 = ?, col_5 = ?, col_6 = ?, col_7 = ?, col_8 = ?, col_9 = ?
        WHERE company_id = ? AND period = ? AND string_code = ?"""
        if isinstance(company_data, CompanyData):
            company_data = [company_data]
        batch_args = []
        for cd in company_data:
            for row_index, row in cd:
                row_args = tuple(row.tolist())
                row_args += (cd.company.id, cd.year)
                row_args += (int(row_index),)
                batch_args.append(row_args)
        if separately:
            for separate_args in batch_args:
                super().commit_async((query, separate_args), lambda _: callback() if callback is not None else None)
        else:
            super().commit_many_async((query, batch_args), lambda _: callback() if callback is not None else None)

    def _get_company_data_async(self, company: Company, period: Optional[str] = None,
                                callback: Optional[Callable[[], None]] = None) -> NoReturn:
        if period is None:
            query = """SELECT * FROM reports WHERE company_id = ?"""
            args = (company.id,)
        else:
            query = """SELECT * FROM reports WHERE company_id = ? AND period = ?"""
            args = (company.id, period)

        def parse_result(rows: List[Tuple]):
            periods = {}
            for row in rows:
                period = row[1]
                if period not in periods:
                    periods[period] = []
                periods[period].append(row[2:])
            for key, value in periods.items():
                company.data[key] = CompanyData(company, key, value)
            if callback is not None:
                callback()
        super().commit_async((query, args), lambda rows: parse_result(rows))

    def get_company_data(self, company: Company, period: Optional[str] = None) -> NoReturn:
        if period is None:
            query = """SELECT * FROM reports WHERE company_id = ?"""
            args = (company.id,)
        else:
            query = """SELECT * FROM reports WHERE company_id = ? AND period = ?"""
            args = (company.id, period)

        rows = super().commit((query, args))
        periods = {}
        for row in rows:
            period = row[1]
            if period not in periods:
                periods[period] = []
            periods[period].append(row[2:])
        for key, value in periods.items():
            company.data[key] = CompanyData(company, key, value)

    def add_period(self, year: str) -> NoReturn:
        query = "INSERT OR IGNORE INTO `available_periods` (year) VALUES (?)"
        super().commit((query, (year,)))

    def remove_period(self, year: str) -> NoReturn:
        query = "DELETE FROM `available_periods` WHERE year = ?"
        super().commit((query, (year,)))

    def is_period_available(self, year: str) -> bool:
        query = "SELECT DISTINCT COUNT() FROM `available_periods` WHERE year = ?"
        return super().commit((query, (year,)))[0][0] > 0

    def get_all_periods(self) -> List[str]:
        query = "SELECT * FROM available_periods"
        periods = super().commit((query, None))
        return [period[0] for period in periods]
