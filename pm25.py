import pymysql
import requests

# 建資料表
tablestr = """
create table if not exists pm25(
id int auto_increment primary key,
site varchar(25),
county varchar(50),
pm25 int,
datacreationdate datetime,
itemunit varchar(20),
unique key site_time (site,datacreationdate)
)
"""
# 新增資料
sqlstr = "insert ignore into pm25 (site,county,pm25,datacreationdate,itemunit)\
      values(%s,%s,%s,%s,%s)"

url = "https://data.moenv.gov.tw/api/v2/aqx_p_02?api_key=540e2ca4-41e1-4186-8497-fdd67024ac44&limit=1000&sort=datacreationdate%20desc&format=JSON"

conn, cursor = None, None


# 開啟DB連線
def open_db():
    global conn, cursor
    try:
        # conn = pymysql.connect(
        # host="localhost", user="root", password="", port=3307, database="demo"
        # )
        conn = pymysql.connect(
            host="mysql-63cdab1-aa8954158-dd04.j.aivencloud.com",
            user="avnadmin",
            password="AVNS_Ukq6fXxTr3Q0YUnS8PX",
            port=24112,
            database="defaultdb",
        )

        # print(conn)
        cursor = conn.cursor()
        print("資料庫開啟成功!")
    except Exception as e:
        print(e)


# 關閉DB連線
def close_db():
    if conn is not None:
        conn.close()
        print("資料庫關閉成功!")


# 抓取open data
def get_open_data():
    resp = requests.get(url, verify=False)
    datas = resp.json()["records"]
    values = [list(data.values()) for data in datas if list(data.values())[2] != ""]
    return values


# 資料寫入資料庫
def write_to_sql():
    try:
        values = get_open_data()
        if len(values) == 0:
            print("目前無資料")
            return

        cursor = conn.cursor()
        size = cursor.executemany(sqlstr, values)
        conn.commit()
        print(f"寫入{size}筆資料成功")
    except Exception as e:
        print(e)


# 從雲端資料庫撈資料出來
def get_data_from_mysql():
    try:
        open_db()
        # 篩選最後更新時間
        # sqlstr = "select max(datacreationdate) from pm25"
        # cursor.execute(sqlstr)
        # max_date = cursor.fetchone()
        # print(max_date)

        sqlstr = (
            "select site,county,pm25,datacreationdate,itemunit "
            "from pm25 "
            "where datacreationdate=(select max(datacreationdate) from pm25);"
        )
        cursor.execute(sqlstr)
        datas = cursor.fetchall()

        return datas
    except Exception as e:
        print(e)
    finally:
        close_db()

    return None


# open_db()
# write_to_sql()
# close_db()

print(get_data_from_mysql())
