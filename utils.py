import sys
import numpy as np
import time;
import zipfile
import os
import hashlib
import colorama
import os
from dotenv import dotenv_values
import uuid
from database import DataBases 


''''
TODO
1)Сделать шифрование файлов
'''

# Местный логгер
class Logger:
    def __init__(self):
        self.config = dotenv_values(".env")
        self.green =colorama.Fore.LIGHTGREEN_EX
        self.yellow = colorama.Fore.LIGHTYELLOW_EX
        self.red =colorama.Fore.RED
        self.ENV = self.config["ENV"]

    def log(self, txt:str):
        if self.ENV == 'develop': print(self.green + txt + colorama.Style.RESET_ALL)

    def process(self, txt:str):
        if self.ENV == 'develop': print(self.yellow + txt + colorama.Style.RESET_ALL)

    def err(self, txt:str):
        if self.ENV == 'develop': print(self.red + txt + colorama.Style.RESET_ALL)

# Метод сохранения файлов
class SaveFile:
    def __init__(self):
        # Размер в 1 мб
        self.N_MB =1024*1024

        # Имена файлов в цикле
        self.files = []

        # Ориганальный размер
        self.orig_size = 0
        
        self.config = dotenv_values(".env")
        self.OUT_PATH = self.config['OUT_PATH']
        self.SOURCE_PATH = self.config["SOURCE_PATH"]
        self.LOGS_PATH = self.config['LOGS_PATH']
        self.ENV = self.config["ENV"]
    
    def __open_and_save_file(self,name:str):
        # Получаем файл
        sourse_file = open(f'{self.SOURCE_PATH}{name}', 'rb')
        this_file = sourse_file.read()
        
        # Определяем количество частей(каждая не более 1мб)
        count_part = (sys.getsizeof(this_file)//self.N_MB)
        self.orig_size = sys.getsizeof(this_file)
        splits = np.array_split(list(this_file),count_part+1)

        # Проходим по частям исходного файла
        for i in range(len(splits)):
            # Делим часть пополам
            first_part = bytes(list(splits[i])[0:len(splits[i])//2])
            second_part = bytes(list(splits[i])[len(splits[i])//2:len(splits[i])])
            # Logger().err("Внимание - пропущен шаг с шифрованием")
            # Сохраняем первую часть
            name_first = str(time.time() * 1000*1000)+f"_p{i+1}e1"

            file_first = open(f"tmp/{name_first}",'wb')
            file_first.write(first_part)
            file_first.close()

            self.files.append(name_first)

            # Сохраняем вторую часть
            name_second = str(time.time() * 1000*1000)+f"_p{i+1}e2"

            file_second = open(f"tmp/{name_second}",'wb')
            file_second.write(second_part)
            file_second.close()

            self.files.append(name_second)
            
            del first_part,second_part,name_first,name_second,file_first,file_second
        self.__clear_tmp()
            
    def __archive_files(self,original:str,name:str,ext:str):
        # Создаем Архив и сохраняем туда наши файлы
       
        filename =f"{uuid.uuid4().hex}.zip"
        result_zip = zipfile.ZipFile(f'{self.OUT_PATH}{filename}', 'w')
        for folder, subfolders, files in os.walk('./tmp'):
            for file in files:
                if file in self.files:
                    result_zip.write(
                        os.path.join(folder, file), 
                        os.path.relpath(os.path.join(folder,file), './tmp'), 
                        compress_type = zipfile.ZIP_DEFLATED
                        )
        result_zip.close()
        del result_zip
        return self.__send_meta(original=original,filename=filename,name=name,ext=ext)

    def __send_meta(self,original:str,filename:str,name:str,ext:str):
        hash = hashlib.md5(open(f'{self.OUT_PATH}{filename}','rb').read()).hexdigest()
        option ={
            "original_filename":f"{original}",
            "filename":filename,
            "hash":hash,
            "original_size":self.orig_size,
            
        }
        file = open(f"{self.LOGS_PATH}log.txt",'a')
        file.write(f"original_filename={original}| filename ={filename}| hash={hash}|\n")
        return option
    
    def __clear_tmp(self):
        i = 1
        for x in self.files:
            print(f"{i}")
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'tmp/{x}')
            print(f"2023-11-01 - {time.time().hex()}   {len(x)*10}   {x}")
            i += 1
            os.remove(path)
        self.files = []
        self.orig_size = 0
    
    def test(self):
        print('test')
    
    def run(self,original:str,name:str,ext:str):
        Logger().log(f'Начинаю обрабатывать файл {name}.{ext}')

        Logger().process('Сохраняю файл...')
        self.__open_and_save_file(f"{name}.{ext}")
        
        Logger().process('Архивирую...')
        data = self.__archive_files(original = original,name=name,ext=ext)

        Logger().process('Очищаю кеш...')
        self.__clear_tmp()

        Logger().log('Готово!')
        return data


class GiveFile:
    def __init__(self):
        pass
    

class DateBasesApi:
    def __init__(self):
        self.config = dotenv_values(".env")
        self.secret = self.config["SECRET_PHASE"]

    def check(self,login:str,password:str):
        in_databases = DataBases().getPasswordByLogin(login)
        if (len(in_databases) == 0): return False
        if (in_databases == None): return False
        print("in_databeses",in_databases)
        profile = {
            "user_id": in_databases[0].get("user_id"),
            "login": in_databases[0].get("login"),
            "surname": in_databases[0].get("surname"),
            "firstname": in_databases[0].get("firstname"),
            "register_date": in_databases[0].get("register_date"),
            "is_admin": in_databases[0].get("is_admin")
        }
        print('fsdfds')
        return (in_databases[0].get("password") == password,profile)

    def getFiels(self,user_id:int):
        return DataBases().getFilesByUserId(user_id=user_id)