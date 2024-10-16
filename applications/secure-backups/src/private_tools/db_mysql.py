import mysql.connector
from mysql.connector import errorcode


class Database:
    def __init__(self, db_secrets):
        self.sql_stmt = ''
        self.clause = ''
        self.left_join = ''
        self.db_config = {
            'user': db_secrets['db_username'],
            'password': db_secrets['db_password'],
            'host': db_secrets['db_host'],
            'port': db_secrets['db_port'],
            'database': db_secrets['db_name'],
            'raise_on_warnings': True
        }
        self.cmd = ''
        try:
            self.db_connect = mysql.connector.connect(**self.db_config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            exit(1)
        else:
            self.db_cursor = self.db_connect.cursor()

    def select(self, tbl_name: str, column_list: list[str] | None):
        if column_list is None:
            columns = '*'
        else:
            columns = ', '.join(column_list)
        self.sql_stmt = f'SELECT {columns} FROM {tbl_name}'
        self.cmd = 'select'

    def insert(self, tbl_name: str, data_set: dict) -> None:
        name_list = '('
        val_list = '('
        for k, v in data_set.items():
            name_list += k + ', '
            if isinstance(v, str):
                val_list += '"' + v + '", '
            elif isinstance(v, int):
                val_list += str(v) + ', '
        name_list = name_list[:-2] + ')'
        val_list = val_list[:-2] + ')'
        self.sql_stmt = f'INSERT INTO {tbl_name} {name_list} VALUES {val_list}'
        self.cmd = 'insert'

    def update(self, tbl_name: str, data_set: dict) -> None:
        set_list = ''
        for k, v in data_set.items():
            if isinstance(v, str):
                set_list += '{key} = "{value}", '.format(key=k, value=v)
            elif isinstance(v, int):
                set_list += '{key} = {value}, '.format(key=k, value=v)
        set_list = set_list[:-2]
        self.sql_stmt = f'UPDATE {tbl_name} SET {set_list}'
        self.cmd = 'update'

    def delete(self, tbl_name: str) -> None:
        self.sql_stmt = f'DELETE FROM {tbl_name}'
        self.cmd = 'delete'

    def close(self) -> None:
        self.db_cursor.close()
        self.db_connect.close()

    def where(self, clause: str) -> None:
        self.clause = clause

    def join_left(self, tbl_name: str, on: str) -> None:
        self.left_join = f'LEFT JOIN {tbl_name} ON ({on})'

    def run(self):
        ex_cmd = f"{self.sql_stmt} {self.left_join} {self.clause}"
        try:
            self.db_cursor.execute(ex_cmd)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            else:
                print(err)
            exit(1)
        else:
            self.db_connect.commit()
            if self.cmd == 'select':
                return self.db_cursor.fetchall()
            elif self.cmd == 'insert':
                return self.db_cursor.lastrowid
            elif self.cmd == 'update':
                return True
            elif self.cmd == 'delete':
                return True
            else:
                return False

    def fetch(self):
        ex_cmd = f"{self.sql_stmt} {self.left_join} {self.clause}"
        try:
            self.db_cursor.execute(ex_cmd)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            else:
                print(err)
            exit(1)
        else:
            self.db_connect.commit()
            return self.db_cursor.fetchone()
