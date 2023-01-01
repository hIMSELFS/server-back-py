import os
# from tkinter import E
from flask import Flask, flash, request, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import dotenv_values
import uuid
import threading, queue
import utils

q = queue.Queue()
app = Flask(__name__)
CORS(app)
config = dotenv_values(".env")
SOURCE_PATH = config["SOURCE_PATH"]
SECRET_KEY = config['SECRET_KEY']

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','exe'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def queue_save():
    while True:
        item = q.get()
        name:str = item['uuid_name']
        utils.Logger().log(f'Working on {item["filename"]}')
        utils.SaveFile().run(original=item["filename"],name=name.split(".")[0],ext=name.split(".")[1])
        utils.Logger().process(f'Finished {item["filename"]}')
        q.task_done()

# Начальная страница
@app.route("/",methods=["GET"])
def home():
    return '''
            <html>
            <body>
            API
            </body>
            </html>
        '''

#Тестируем fetch
@app.route('/get/test',methods=["GET","POST"])
def test():
	response ={"test":'value'}
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
    app.run(host='0.0.0.0', port=7777)

