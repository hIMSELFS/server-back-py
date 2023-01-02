from getpass import getpass
from mysql.connector import connect, Error
from dotenv import dotenv_values


class DataBases:
    def __init__(self):
        self.config = dotenv_values(".env")
        self.host = self.config["MYSQL_HOST"]
        self.user = self.config["MYSQL_USER"]
        self.password = self.config["MYSQL_PASS"]
        self.db = self.config["MYSQL_DB"]

    def getPasswordByLogin(self,login:str):
        try:
            with connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f'''
                    SELECT password FROM users WHERE login = '{login}'
                    ''')
                    data = cursor.fetchone()
                    if (data == None):
                        return None
                    else:
                        return data[0]
        except Error as e:
            return None

