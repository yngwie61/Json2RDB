import sqlite3
import numpy as np
import json
import timeit

def selectDB(id, cursor):
    # JSONデータをデータベースに挿入
    select_query = f"SELECT * FROM dummy WHERE id = ? LIMIT 1"
    cursor.execute(select_query, (id,))
    result = cursor.fetchall()[0]
    result_json = {
        "id": id,
        "key1": result[1],
        "key2": result[2],
        "key3": result[3]
    }
    return result_json


def updateDB(diff_json, cursor):
    key_query_array = []
    value_array = []
    id = diff_json["id"]
    for key in list(diff_json.keys()):
        if key != "id":
            key_query_array.append(f"{key} = ?")
            value_array.append(diff_json[key])
    if len(key_query_array) == 0:
        return False

    else:
        key_query = ', '.join(key_query_array)
        value_tuple = tuple(value_array)
        # JSONデータをデータベースに挿入
        update_query = f"UPDATE dummy SET {key_query} WHERE id = {id}"
        cursor.execute(update_query, value_tuple)

        return True

def validateJson(current_json_data, new_json_data):
    list1 = list(current_json_data.keys())
    list2 = list(new_json_data.keys())
    key_diff = np.setdiff1d(list1, list2)
    if len(key_diff) == 0:
        return True
    else:
        ### もしkey diffがあったら処理は中断すべき
        return False

def getDiffFronJson(current_json_data, new_json_data):
    if (current_json_data["id"] == new_json_data["id"]):
        if validateJson(current_json_data, new_json_data):
            id = current_json_data["id"]
            diff_json = {}
            update_json = {"id": id}
            for key in list(current_json_data.keys()):
                if current_json_data[key] != new_json_data[key]:
                    diff_json[key] = {"old": current_json_data[key], "new": new_json_data[key]}
                    update_json[key] = new_json_data[key]
            # 差分をSQLでUPDATEしたら良い
            return update_json, diff_json
        else:
            raise Exception("Json Schema Error")


def main():
    # SQLiteデータベースに接続
    connection = sqlite3.connect('db/test.db')
    cursor = connection.cursor()

    # DBからの読み込み
    target_key = 1
    current_json_data = selectDB(target_key, cursor)
    print(f"before update data: {current_json_data}")
    with open('update.json') as file:
        new_json_data = json.load(file)
        print(f"new json data: {new_json_data}")
        update_json, diff_json = getDiffFronJson(current_json_data, new_json_data)
        updateDB(update_json, cursor)

    print(f"diff data: {update_json}")
    print(f"after update data: {selectDB(target_key, cursor)}")

    # コミットと接続のクローズ
    connection.commit()
    connection.close()

# 実行時間を計測
execution_time = timeit.timeit(main, number=1) * 1000 # msec変換
print(f"処理時間: {execution_time} ミリ秒")