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

    def select(self, tbl_name: str, column_list: list[str] | None) -> None:
        if column_list is None:
            columns = '*'
        else:
            columns = ', '.join(column_list)
        self.sql_stmt = 'SELECT ' + columns + ' FROM ' + tbl_name

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

        self.sql_stmt = 'INSERT INTO ' + tbl_name + ' ' + name_list + ' VALUES ' + val_list

    def update(self, tbl_name: str, data_set: dict) -> None:
        set_list = ''
        for k, v in data_set.items():
            if isinstance(v, str):
                set_list += '{key} = "{value}", '.format(key=k, value=v)
            elif isinstance(v, int):
                set_list += '{key} = {value}, '.format(key=k, value=v)
        set_list = set_list[:-2]
        self.sql_stmt = 'UPDATE ' + tbl_name + ' SET ' + set_list

    def delete(self, tbl_name: str) -> None:
        self.sql_stmt = 'DELETE FROM ' + tbl_name

    def close(self) -> None:
        self.db_cursor.close()
        self.db_connect.close()

    def where(self, clause: str) -> None:
        self.clause = clause

    def join_left(self, tbl_name: str, on: str) -> None:
        self.left_join = 'LEFT JOIN ' + tbl_name + ' ON (' + on + ')'

    def run(self):
        if self.left_join != '':
            self.sql_stmt += ' ' + self.left_join
        if self.clause != '':
            self.sql_stmt += ' ' + self.clause
        try:
            self.db_cursor.execute(self.sql_stmt)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            else:
                print(err)
            exit(1)
        else:
            self.db_connect.commit()
