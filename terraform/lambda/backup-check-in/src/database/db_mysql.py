import mysql.connector
from mysql.connector import errorcode


class Database:
    def __init__(self, db_secrets):
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

    def insert(self, tbl_name: str, data_set: dict):
        name_list = '('
        val_list = '('
        for key, value in data_set.items():
            name_list += key + ', '
            if isinstance(value, str):
                val_list += '"' + value + '", '
            elif isinstance(value, int):
                val_list += str(value) + ', '
        name_list = name_list[:-2] + ')'
        val_list = val_list[:-2] + ')'

        sql_stmt = 'INSERT INTO ' + tbl_name + ' ' + name_list + ' VALUES ' + val_list
        print(sql_stmt)
        try:
            self.db_cursor.execute(sql_stmt)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            else:
                print(err)
            exit(1)
        else:
            self.db_connect.commit()
            return self.db_cursor.lastrowid

    def update(self, tbl_name: str, data_set: dict):
        pass

    def delete(self):
        pass

    def close(self):
        self.db_cursor.close()
        self.db_connect.close()
