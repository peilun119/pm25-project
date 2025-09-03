from flask import Flask, render_template, Response
from datetime import datetime
from pm25 import (
    get_data_from_mysql,
    write_data_to_mysql,
    get_avg_pm25_from_mysql,
    get_pm25_by_conty,
)
import json

# from pm25 import get_open_data

books = {
    1: {
        "name": "Python book",
        "price": 299,
        "image_url": "https://im2.book.com.tw/image/getImage?i=https://www.books.com.tw/img/CN1/136/11/CN11361197.jpg&v=58096f9ck&w=348&h=348",
    },
    2: {
        "name": "Java book",
        "price": 399,
        "image_url": "https://im1.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/087/31/0010873110.jpg&v=5f7c475bk&w=348&h=348",
    },
    3: {
        "name": "C# book",
        "price": 499,
        "image_url": "https://im1.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/036/04/0010360466.jpg&v=62d695bak&w=348&h=348",
    },
}


app = Flask(__name__)  # 以此檔案當作程式起始點


@app.route("/county-pm25/<county>")
def get_county_pm25(county):
    result = get_pm25_by_conty(county)

    if len(result) == 0:
        return Response(
            json.dumps(
                {"result": "取得資料失敗", "message": f"無此[{county}]縣市"},
                ensure_ascii=False,
            )
        )

    site = [r[0] for r in result]  # 第一個欄位是城市
    pm25 = [float(r[1]) for r in result]  # 第二個欄位是pm25 轉浮點數
    datetime = result[0][2].strftime("%Y-%m-%d %H:%M:%S")  # 將時間轉為字串
    # print(datetime)

    return Response(
        json.dumps(
            {
                "county": county,
                "count": len(site),
                "site": site,
                "pm25": pm25,
                "datetime": datetime,
            },
            ensure_ascii=False,
        ),
        mimetype="application/json",
    )  # Response 封裝, mimetype="application/json" 是封裝成json 格式


@app.route("/avg-pm25")
def get_avg_pm25():
    result = get_avg_pm25_from_mysql()
    county = [r[0] for r in result]  # 第一個欄位是城市
    pm25 = [float(r[1]) for r in result]  # 第二個欄位是pm25 轉浮點數

    return Response(
        json.dumps({"county": county, "pm25": pm25}, ensure_ascii=False),
        mimetype="application/json",
    )  # Response 封裝, mimetype="application/json" 是封裝成json 格式


@app.route("/update-db")
def update_db():
    result = write_data_to_mysql()
    # 用json.dumps()顯示中文字,ensure_ascii=False 是不要用ascii 編碼
    return json.dumps(result, ensure_ascii=False)


@app.route("/pm25")
def get_pm25():
    # values = get_open_data()
    values = get_data_from_mysql()
    print(values)
    columns = ["站點名稱", "縣市", "PM2.5", "更新時間", "單位"]
    return render_template("pm25.html", values=values, columns=columns)


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
        # books = {1: "Python book", 2: "Java book", 3: "Flask book"}

        if id == None:  # 沒帶參數 傳回所有書籍
            # return books
            return render_template("books.html", books=books)

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
    # return "<h1>這是首頁!</h1>"
    timenow = now_time()
    return render_template("index.html", time=timenow)  # 回傳網頁模板及參數 到前端網頁


app.run(debug=True)  # 程式的尾端
