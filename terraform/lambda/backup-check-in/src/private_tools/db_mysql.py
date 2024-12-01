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
        for k, v in data_set.items():
            name_list += k + ', '
            if isinstance(v, str):
                val_list += '"' + v + '", '
            elif isinstance(v, int):
                val_list += str(v) + ', '
            elif isinstance(v, float):
                val_list += str(v) + ', '
        name_list = name_list[:-2] + ')'
        val_list = val_list[:-2] + ')'

        try:
            self.db_cursor.execute(f'INSERT INTO {tbl_name} {name_list} VALUES {val_list}')
        except mysql.connector.Error as err:
            raise err
        self.db_connect.commit()
        return self.db_cursor.lastrowid

    def update(self, tbl_name: str, data_set: dict, where: str):
        set_list = ''
        for k, v in data_set.items():
            if isinstance(v, str):
                set_list += f'{k} = "{v}", '
            elif isinstance(v, int):
                set_list += f'{k} = {v}, '
            elif isinstance(v, float):
                set_list += f'{k} = {v}, '
        set_list = set_list[:-2]
        try:
            self.db_cursor.execute(f'UPDATE {tbl_name} SET {set_list} WHERE {where}')
        except mysql.connector.Error as err:
            raise err
        self.db_connect.commit()
        return True

    def select(self, tbl_name: str, fields: list, where: str = ''):
        if len(fields) > 0:
            field_list = ', '.join(fields)
        else:
            field_list = '*'
        try:
            self.db_cursor.execute(f'SELECT {field_list} FROM {tbl_name} WHERE {where}')
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            else:
                raise err
        else:
            fetched_rows = self.db_cursor.fetchall()
            if len(fetched_rows) == 0:
                result =  fetched_rows
            else:
                colums = [i[0] for i in self.db_cursor.description]
                result = [dict(zip(colums, rows)) for rows in fetched_rows]
            return result

    def delete(self):
        pass

    def close(self):
        self.db_cursor.close()
        self.db_connect.close()
