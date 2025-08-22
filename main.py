from flask import Flask
from datetime import datetime


app = Flask(__name__)  # 以此檔案當作程式起始點


@app.route("/bmi/height=<h>&weight=<w>")
def get_bmi(h, w):
    bmi = round(eval(w) / (eval(h) / 100) ** 2, 2)
    return f"<h1>身高:{h}cm 體重:{w}kg <br>BMI={bmi}</h1>"


# 網址沒帶參數與有帶參數可以寫一起
# 網址後面帶<參數> 參數預設為字串,若要設為其他型態,需要註明
@app.route("/books")
@app.route("/books/id=<int:id>")
def get_books(id=None):
    try:
        books = {1: "Python book", 2: "Java book", 3: "Flask book"}

        if id == None:  # 沒帶參數 傳回所有書籍
            return books

        return books[id]
    except Exception as e:
        return f"書籍編號錯誤:{e}"


@app.route("/nowtime")
def now_time():
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 將時間轉為字串
    # print(time)
    return time  # 不轉型會報錯 The return type must be a string, dict, list, tuple


# route 綁定 網址跟方法
# '/' 是首頁的意思
# 最後一定要將資料return出去才會顯示在網頁上
@app.route("/")
def index():
    return "<h1>這是首頁!</h1>"


app.run(debug=True)  # 程式的尾端
