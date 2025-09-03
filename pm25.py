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
        # 沒資料表就建表
        cursor.execute(tablestr)
        conn.commit()
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

        size = cursor.executemany(sqlstr, values)
        conn.commit()
        print(f"寫入{size}筆資料成功")

        return size
    except Exception as e:
        print(e)

    return 0


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

        # 取得不重複縣市名稱-20250903
        sqlstr = "select distinct county from pm25;"
        cursor.execute(sqlstr)
        # 轉為一維的資料
        countys = [county[0] for county in cursor.fetchall()]

        return datas, countys
    except Exception as e:
        print(e)
    finally:
        close_db()

    return None


# 整合更新資料庫
def write_data_to_mysql():
    try:
        open_db()
        size = write_to_sql()

        return {"結果": "success", "寫入筆數": size}

    except Exception as e:
        print(e)

        return {"結果": "failure", "message": str(e)}

    finally:
        close_db()


# 取得各縣市站點的平均值函式
def get_avg_pm25_from_mysql():
    try:
        open_db()
        sqlstr = """
        select county,round(avg(pm25),2) from pm25 group by county;
        """
        cursor.execute(sqlstr)
        datas = cursor.fetchall()

        return datas
    except Exception as e:
        print(e)
    finally:
        close_db()

    return None


# 取得單一縣市的站點數值
def get_pm25_by_conty(county):
    try:
        open_db()

        # 取得最新時間的資料
        sqlstr = (
            "select site,pm25,datacreationdate from pm25 "
            "where county=%s "
            "and datacreationdate=(select max(datacreationdate) from pm25);"
        )

        cursor.execute(sqlstr, (county,))
        datas = cursor.fetchall()

        return datas
    except Exception as e:
        print(e)
    finally:
        close_db()

    return None


if __name__ == "__main__":
    # write_data_to_mysql()
    # print(get_avg_pm25_from_mysql())
    # print(get_pm25_by_conty("臺南市"))
    print(get_data_from_mysql())
