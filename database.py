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
                    SELECT  
                        t1.user_id,
                        t1.password,
                        t1.login,
                        t1.surname,
                        t1.firstname,
                        DATE_FORMAT(t1.register_date, "%Y-%m-%d") AS register_date,
                        t1.is_admin
                    FROM users t1
                    WHERE t1.login = '{login}'
                    ''')
                    data = cursor.fetchall()
                    row_headers=[x[0] for x in cursor.description]
                    if (data == None):
                        return None
                    else:
                        json_data=[]
                        for result in data:
                            json_data.append(dict(zip(row_headers,result)))
                        print(json_data)  
                        return json_data
        except Error as e:
            return None

    def getFilesByUserId(self,user_id:int):
        try:
            with connect(   
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(f'''
                   SELECT
                    	t1.id,
                        t1.user_id,
                        t1.filename,
                        t1.secret,
                        t1.is_deleted,
                        DATE_FORMAT(t1.created_at, "%Y-%m-%d %H:%i:%S") AS created_at 
                   FROM data_files t1 WHERE t1.is_deleted <> 1 AND t1.user_id = {user_id}
                    ''')
                    data = cursor.fetchall()
                    row_headers=[x[0] for x in cursor.description]
                    if (data == None):
                        return None
                    else:
                        json_data=[]
                        for result in data:
                            json_data.append(dict(zip(row_headers,result)))
                            
                        return json_data
        except Error as e:
            return None