import os
from re import U
from cv2 import log
# from urllib import response
from flask import Flask, flash, request,Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import dotenv_values
import uuid
import threading, queue
from utils import Logger,SaveFile,DateBasesApi
import json
import logging 
from database import DataBases 

q = queue.Queue()
app = Flask(__name__)
CORS(app)
config = dotenv_values(".env")
SOURCE_PATH ="./incoming/"
SECRET_KEY = config['SECRET_KEY']

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','exe'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def queue_save():
    while True:
        item = q.get()
        name:str = item['uuid_name']
        Logger().log(f'Working on {item["filename"]}')
        SaveFile().run(original=item["filename"],name=name.split(".")[0],ext=name.split(".")[1])
        Logger().process(f'Finished {item["filename"]}')
        q.task_done()

# Начальная страница
@app.route("/",methods=["GET"])
def home():
    response = json.dumps({'API':"V1.1"})
    return response

#!!!Авторизация!!! 
@app.route('/check/pass',methods=["POST"])
def check_pass():
    # Проверяем, есть ли данные в запросе
    if (len(request.data) == 0):
        response ={ "status":False, "checked":False, "error":"Не переданы обязательные параметры" }
        return  Response(json.dumps(response), mimetype='application/json',status=400)

    # Проверяем наличие пароля
    password = request.json.get("password")
    if (password == None):
        response ={ "status":False, "checked":False,  "error":"Не передан пароль" }
        return  Response(json.dumps(response), mimetype='application/json',status=400)
    
    # Проверяем наличие логина
    login =request.json.get("login")
    if (login == None):
        response = { "status":False,  "checked":False, "error":"Не передан логин" }
        return Response(json.dumps(response), mimetype='application/json',status=400)
    
    result = DateBasesApi().check(login=login,password=password)
    if (result == False): 
         response = { "status":True, "checked":False,"data":[], "error":"" }
         return Response(json.dumps(response), mimetype='application/json',status=200)
    
    response = { "status":True, "checked":result[0],"data":result[1], "error":"" }
    return Response(json.dumps(response), mimetype='application/json',status=200)


#!!!Получение файлов для пользователя!!!
@app.route("/get/files",methods=["POST"])
def get_all_files():
    # Проверяем получение данных
    if (len(request.data) == 0):
        response ={ "status":False, "checked":False, "error":"Не переданы обязательные параметры: user_id" }
        return  Response(json.dumps(response), mimetype='application/json',status=400)

    # Проверяем наличие пароля
    user_id = request.json.get("user_id")
    if (user_id == None):
        response ={ "status":False, "checked":False,  "error":"Не передан user_id" }
        return  Response(json.dumps(response), mimetype='application/json',status=400)
    
    result = DateBasesApi().getFiels(user_id=user_id)
    response = { "status":True, "data":result, "error":"" }

    return Response(json.dumps(response), mimetype='application/json',status=200)




# test
@app.route("/test",methods=["GET","POST"])
def test():
    result = DataBases().getPasswordByLogin(login="valery.azarov")
    Logger().log(txt="Готово")
    response = json.dumps({'data':result})
    return response


# Загружаем файл
@app.route("/load", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Проверка на наличие файла    
        print('req',request.files)
        if 'file' not in request.files:
            flash('No file part')
            print("Нет файла")
            return '''
            <html><body>Файл не выбран</body></html>
            '''

        file = request.files['file']
        
        # Нет имени файла
        if file.filename == '':
            flash('No selected file')
            return '''
            <html><body>Файл не выбран</body></html>
            '''
        
        # Нет расширения
        if file.filename.find('.') == -1:
            flash('No have ext')
            return '''
            <html><body>Файл без расширения</body></html>
            '''
        
        # Проверяем тип файла
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            uuid_name =f"{uuid.uuid4().hex}.{filename.split('.')[1]}"
            file.save(os.path.join(f"{SOURCE_PATH}{uuid_name}"))
            q.put({"filename":filename,"uuid_name":uuid_name})
            return '''
            <html><body>Готово</body></html>
            '''

    if request.method == 'GET':
        return '''
            <html>
            <body>
            Разрешен только POST
            </body>
            </html>
        '''


if __name__ == "__main__":
    # Запускаем очередь
    threading.Thread(target=queue_save, daemon=True).start()
    app.secret_key = SECRET_KEY
    app.debug = False
    # app.logger.disabled = True
    # log = logging.getLogger('werkzeug')
    # log.disabled = True
    app.run(host='0.0.0.0', port=7777)

